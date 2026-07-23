import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../models/customer_model.dart';
import '../models/product_model.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';

class CreateQuotationPage extends StatefulWidget {
  final String? customerId;
  final String? draftId;

  const CreateQuotationPage({super.key, this.customerId, this.draftId});

  @override
  State<CreateQuotationPage> createState() => _CreateQuotationPageState();
}

class _CreateQuotationPageState extends State<CreateQuotationPage> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final _lineItems = <_LineItem>[];
  bool _loading = false;
  bool _isEditing = false;
  String? _draftId;
  Client? _selectedClient;
  bool _pickingClient = false;
  bool _loadingClient = false;

  @override
  void initState() {
    super.initState();
    if (widget.draftId != null) {
      _loadDraft();
    } else if (widget.customerId != null) {
      _loadCustomer();
    } else {
      WidgetsBinding.instance.addPostFrameCallback((_) => _pickClient());
    }
  }

  Future<void> _loadCustomer() async {
    setState(() => _loadingClient = true);
    final api = context.read<ApiService>();
    try {
      final customerId = int.parse(widget.customerId!);
      final data = await api.getCustomer(customerId);
      if (mounted) setState(() {
        _selectedClient = Client.fromJson(data);
        _loadingClient = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loadingClient = false);
      if (mounted) _pickClient();
    }
  }

  Future<void> _loadDraft() async {
    setState(() => _loadingClient = true);
    final api = context.read<ApiService>();
    try {
      final draft = await api.getDraft(widget.draftId!);
      if (draft == null || !mounted) return;
      _isEditing = true;
      _draftId = widget.draftId;
      _version = draft['version'] as int? ?? 1;
      _descriptionController.text = draft['notes'] as String? ?? '';

      if (draft['customer_id'] != null) {
        final customers = await api.getCustomers();
        Client match;
        try {
          match = customers
              .map((j) => Client.fromJson(j))
              .firstWhere((c) => c.id == draft['customer_id']);
        } catch (_) {
          match = Client(
            id: draft['customer_id'] as int,
            odooId: 0,
            name: draft['customer_name'] as String? ?? 'Cliente',
          );
        }
        if (mounted) _selectedClient = match;
      }

      final lines = draft['lines'] as List<dynamic>? ?? [];
      for (final line in lines) {
        final productId = line['product_id'] as int;
        final products = await api.getProducts();
        final product = products
            .map((j) => Product.fromJson(j))
            .firstWhere((p) => p.id == productId,
                orElse: () => Product(
                    id: productId,
                    odooId: line['product_odoo_id'] as int? ?? 0,
                    name: line['product_name'] as String? ?? 'Producto #$productId',
                    listPrice: (line['unit_price'] as num).toDouble()));
        _lineItems.add(_LineItem(
          product: product,
          quantity: (line['quantity'] as num).toDouble(),
        ));
      }
      if (mounted) setState(() => _loadingClient = false);
    } catch (_) {
      if (mounted) setState(() => _loadingClient = false);
    }
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _addProduct() async {
    final api = context.read<ApiService>();
    try {
      final data = await api.getProducts();
      final products = data.map((j) => Product.fromJson(j)).toList();

      if (!mounted) return;

      final selected = await showDialog<Product>(
        context: context,
        builder: (ctx) => _ProductDialog(products: products),
      );

      if (selected != null) {
        setState(() {
          _lineItems.add(_LineItem(product: selected));
        });
      }
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al cargar productos')),
      );
    }
  }

  int _version = 1;

  Map<String, dynamic> _buildPayload() {
    final payload = <String, dynamic>{
      'customer_id': _selectedClient!.id,
      'notes': _descriptionController.text,
      'lines': _lineItems.map((item) => {
        'product_id': item.product.id,
        'quantity': item.quantity,
        'unit_price': item.product.listPrice,
        'tax_id': item.product.taxesId,
      }).toList(),
    };
    if (_isEditing) {
      payload['version'] = _version;
    }
    return payload;
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_lineItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Agregá al menos un producto')),
      );
      return;
    }
    if (_selectedClient == null) return;

    setState(() => _loading = true);

    final api = context.read<ApiService>();
    try {
      if (_isEditing) {
        await api.updateDraft(_draftId!, _buildPayload());
      } else {
        final draft = await api.createDraft(_buildPayload());
        _draftId = draft['id'] as String;
        _isEditing = true;
      }

      if (!mounted) return;
      context.read<ApiService>().ordersRefreshNotifier.value++;
      context.go('/quotations/$_draftId');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: const Text('Borrador guardado correctamente'), backgroundColor: AppColors.primary, behavior: SnackBarBehavior.floating),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}'), backgroundColor: AppColors.error),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _submitAndGenerate() async {
    if (!_formKey.currentState!.validate()) return;
    if (_lineItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Agregá al menos un producto')),
      );
      return;
    }
    if (_selectedClient == null) return;

    setState(() => _loading = true);

    final api = context.read<ApiService>();
    try {
      if (_isEditing) {
        await api.updateDraft(_draftId!, _buildPayload());
        await api.generateQuotation(_draftId!);
      } else {
        final draft = await api.createDraft(_buildPayload());
        final draftId = draft['id'] as String;
        await api.generateQuotation(draftId);
      }

      if (!mounted) return;
      context.read<ApiService>().ordersRefreshNotifier.value++;
      context.go('/quotations');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: const Text('Cotización generada correctamente'), backgroundColor: AppColors.primary, behavior: SnackBarBehavior.floating),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}'), backgroundColor: AppColors.error),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _editCustomer() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        content: Text('Pendiente implementar', style: GoogleFonts.inter()),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cerrar')),
        ],
      ),
    );
  }

  Future<void> _pickClient() async {
    setState(() => _pickingClient = true);
    await _showCustomerPicker();
    if (mounted && _selectedClient == null) {
      context.go('/quotations');
    }
  }

  Future<void> _showCustomerPicker() async {
    final api = context.read<ApiService>();
    try {
      final data = await api.getCustomers();
      final clients = data.map((j) => Client.fromJson(j)).toList();
      if (!mounted) return;

      final selected = await showDialog<Client>(
        context: context,
        builder: (ctx) => _CustomerPickerDialog(clients: clients),
      );
      if (selected != null) {
        setState(() {
          _selectedClient = selected;
          _pickingClient = false;
        });
      }
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al cargar clientes')),
      );
    }
  }

  void _newCustomer() {
    context.push('/clients/new');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.go('/quotations'),
        ),
        title: Text(_isEditing ? 'Editar cotización' : 'Nueva cotización', style: GoogleFonts.inter(fontWeight: FontWeight.w700)),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 0,
        actions: [
          OutlinedButton.icon(
            onPressed: _loading ? null : _submit,
            icon: _loading
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.save_outlined),
            label: const Text('Guardar'),
          ),
          const SizedBox(width: 8),
          FilledButton.icon(
            onPressed: _loading ? null : _submitAndGenerate,
            icon: _loading
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.rocket_launch),
            label: const Text('Generar cotización'),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: _selectedClient == null || _loadingClient
          ? Center(
              child: CircularProgressIndicator(color: AppColors.primary),
            )
          : context.isDesktop
              ? Padding(
                  padding: const EdgeInsets.all(24),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(flex: 3, child: _buildLeftPanel()),
                      const SizedBox(width: 24),
                      SizedBox(width: 350, child: _buildClientCard()),
                    ],
                  ),
                )
              : _buildMobileBody(),
    );
  }

  Widget _buildMobileBody() {
    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildClientCard(),
          const SizedBox(height: 20),
          _buildDescriptionCard(),
          const SizedBox(height: 20),
          _buildProductsCard(),
          const SizedBox(height: 20),
          _buildTotalsCard(),
        ],
      ),
    );
  }

  Widget _buildLeftPanel() {
    return Form(
      key: _formKey,
      child: ListView(
        children: [
          _buildDescriptionCard(),
          const SizedBox(height: 24),
          _buildProductsCard(),
          const SizedBox(height: 24),
          _buildTotalsCard(),
        ],
      ),
    );
  }

  Widget _buildDescriptionCard() {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Descripción', style: GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 18, color: AppColors.textPrimary)),
            const SizedBox(height: 16),
            TextFormField(
              controller: _descriptionController,
              maxLines: 2,
              decoration: const InputDecoration(
                hintText: 'Descripción de la cotización',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductsCard() {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text('Productos', style: GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 18, color: AppColors.textPrimary)),
                const Spacer(),
                FilledButton.icon(
                  onPressed: _addProduct,
                  icon: const Icon(Icons.add),
                  label: const Text('Agregar producto'),
                ),
              ],
            ),
            const SizedBox(height: 20),
            if (_lineItems.isEmpty)
              SizedBox(
                height: 140,
                child: Center(
                  child: Text('Todavía no agregaste productos.', style: GoogleFonts.inter(color: AppColors.textSecondary)),
                ),
              )
            else
              _buildProductsTable(),
          ],
        ),
      ),
    );
  }

  Widget _buildProductsTable() {
    return LayoutBuilder(builder: (context, constraints) {
      final isWide = constraints.maxWidth > 700;
      final table = Column(
        children: [
          _productTableHeader(isWide),
          if (isWide)
            ..._lineItems.asMap().entries.map((entry) => _buildProductRowWide(entry.key, entry.value))
          else
            ..._lineItems.asMap().entries.map((entry) => _buildProductRowNarrow(entry.key, entry.value)),
        ],
      );
      if (isWide) return table;
      return SingleChildScrollView(scrollDirection: Axis.horizontal, child: table);
    });
  }

  Widget _productTableHeader(bool isWide) {
    final style = GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary);
    if (isWide) {
      return Container(
        decoration: BoxDecoration(color: AppColors.background, borderRadius: BorderRadius.circular(8)),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        child: Row(
          children: const [
            Expanded(flex: 3, child: Text('Producto', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Cantidad', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Precio', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Subtotal', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('IVA', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Total', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
            SizedBox(width: 40),
          ],
        ),
      );
    }
    return Container(
      decoration: BoxDecoration(color: AppColors.background, borderRadius: BorderRadius.circular(8)),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      child: Row(
        children: [
          SizedBox(width: 160, child: Text('Producto', style: style)),
          SizedBox(width: 80, child: Text('Cantidad', style: style)),
          SizedBox(width: 80, child: Text('Precio', style: style)),
          SizedBox(width: 80, child: Text('Subtotal', style: style)),
          SizedBox(width: 80, child: Text('IVA', style: style)),
          SizedBox(width: 80, child: Text('Total', style: style)),
          SizedBox(width: 40),
        ],
      ),
    );
  }

  Widget _buildProductRowWide(int index, _LineItem item) {
    return Container(
      decoration: BoxDecoration(border: Border(bottom: BorderSide(color: AppColors.divider.withValues(alpha: 0.3)))),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: Row(
        children: [
          Expanded(flex: 3, child: Text(item.product.name, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
          Expanded(flex: 1, child: _qtyStepper(item)),
          Expanded(flex: 1, child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Text('\$${item.product.listPrice.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
          )),
          Expanded(flex: 1, child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Text('\$${item.lineSubtotal.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
          )),
          Expanded(flex: 1, child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: item.taxRate > 0
                ? Text('\$${item.lineTax.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))
                : Text('—', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
          )),
          Expanded(flex: 1, child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Text('\$${item.lineTotal.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.primary)),
          )),
          SizedBox(width: 40, child: IconButton(icon: const Icon(Icons.close, size: 16), onPressed: () => setState(() => _lineItems.removeAt(index)))),
        ],
      ),
    );
  }

  Widget _buildProductRowNarrow(int index, _LineItem item) {
    return Container(
      decoration: BoxDecoration(border: Border(bottom: BorderSide(color: AppColors.divider.withValues(alpha: 0.3)))),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: Row(
        children: [
          SizedBox(width: 160, child: Text(item.product.name, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
          SizedBox(width: 100, child: _qtyStepper(item)),
          SizedBox(width: 80, child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Text('\$${item.product.listPrice.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
          )),
          SizedBox(width: 80, child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Text('\$${item.lineSubtotal.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
          )),
          SizedBox(width: 80, child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: item.taxRate > 0
                ? Text('\$${item.lineTax.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))
                : Text('—', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
          )),
          SizedBox(width: 80, child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Text('\$${item.lineTotal.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.primary)),
          )),
          SizedBox(width: 40, child: IconButton(icon: const Icon(Icons.close, size: 16), onPressed: () => setState(() => _lineItems.removeAt(index)))),
        ],
      ),
    );
  }

  Widget _qtyStepper(_LineItem item) {
    return Row(
      children: [
        _stepperBtn(Icons.remove, () {
          if (item.quantity > 1) setState(() => item.quantity--);
        }),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: Text('${item.quantity}', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
        ),
        _stepperBtn(Icons.add, () {
          setState(() => item.quantity++);
        }),
      ],
    );
  }

  Widget _stepperBtn(IconData icon, VoidCallback onPressed) {
    return SizedBox(
      width: 28,
      height: 28,
      child: IconButton(
        padding: EdgeInsets.zero,
        icon: Icon(icon, size: 16),
        onPressed: onPressed,
        style: IconButton.styleFrom(
          backgroundColor: AppColors.background,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
      ),
    );
  }

  Widget _buildTotalsCard() {
    final subtotal = _lineItems.fold<double>(0.0, (s, i) => s + i.lineSubtotal);
    final iva = _lineItems.fold<double>(0.0, (s, i) => s + i.lineTax);
    final total = subtotal + iva;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            _totalRow('Subtotal', subtotal),
            const SizedBox(height: 6),
            _totalRow('IVA', iva),
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Divider(height: 1),
            ),
            _totalRow('TOTAL', total, big: true),
          ],
        ),
      ),
    );
  }

  Widget _totalRow(String title, double value, {bool big = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(
            title,
            style: GoogleFonts.inter(
              fontSize: big ? 18 : 15,
              fontWeight: big ? FontWeight.bold : FontWeight.w500,
              color: AppColors.textPrimary,
            ),
          ),
          const Spacer(),
          Text(
            '\$${value.toStringAsFixed(2)}',
            style: GoogleFonts.inter(
              fontSize: big ? 22 : 16,
              fontWeight: big ? FontWeight.bold : FontWeight.w700,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildClientCard() {
    final c = _selectedClient!;
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: AppColors.primary.withValues(alpha: 0.12),
                  child: Text(
                    c.initials,
                    style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.primary),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(c.name, style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                      if (c.companyName.isNotEmpty)
                        Text(c.companyName, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (c.email.isNotEmpty) _clientInfoRow(Icons.email_outlined, c.email),
            if (c.phone.isNotEmpty) _clientInfoRow(Icons.phone_outlined, c.phone),
            if (c.address.isNotEmpty) _clientInfoRow(Icons.location_on_outlined, c.address),
            if (c.cuit.isNotEmpty) _clientInfoRow(Icons.badge_outlined, 'CUIT: ${c.cuit}'),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: FilledButton.tonalIcon(
                onPressed: _showCustomerPicker,
                icon: const Icon(Icons.swap_horiz, size: 18),
                label: const Text('Cambiar cliente'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _clientInfoRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Icon(icon, size: 16, color: AppColors.textSecondary),
          const SizedBox(width: 8),
          Expanded(
            child: Text(text, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
          ),
        ],
      ),
    );
  }
}

class _LineItem {
  final Product product;
  int quantity;

  _LineItem({required this.product, double? quantity})
    : quantity = (quantity ?? 1).toInt();

  double get taxRate => product.taxesRate;

  double get lineSubtotal => quantity * product.listPrice;
  double get lineTax => lineSubtotal * taxRate / 100;
  double get lineTotal => lineSubtotal + lineTax;
}

class _ProductDialog extends StatefulWidget {
  final List<Product> products;
  const _ProductDialog({required this.products});

  @override
  State<_ProductDialog> createState() => _ProductDialogState();
}

class _ProductDialogState extends State<_ProductDialog> {
  final _searchController = TextEditingController();
  late List<Product> _filtered;

  @override
  void initState() {
    super.initState();
    _filtered = widget.products;
    _searchController.addListener(_filter);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _filter() {
    final q = _searchController.text.toLowerCase();
    setState(() {
      _filtered = q.isEmpty
          ? widget.products
          : widget.products.where((p) =>
              p.name.toLowerCase().contains(q) ||
              p.defaultCode.toLowerCase().contains(q) ||
              p.barcode.toLowerCase().contains(q)).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520, maxHeight: 600),
        child: Material(
          borderRadius: BorderRadius.circular(18),
          color: AppColors.surface,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text('Seleccionar producto', style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    hintText: 'Buscar por nombre, código o barra...',
                    prefixIcon: Icon(Icons.search),
                    isDense: true,
                  ),
                ),
                const SizedBox(height: 12),
                Expanded(
                  child: _filtered.isEmpty
                      ? Center(
                          child: Text('Sin resultados', style: GoogleFonts.inter(color: AppColors.textSecondary)),
                        )
                      : ListView.separated(
                          itemCount: _filtered.length,
                          separatorBuilder: (_, __) => const Divider(height: 1),
                          itemBuilder: (ctx, i) {
                            final p = _filtered[i];
                            return ListTile(
                              title: Text(p.name, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500)),
                              subtitle: Row(
                                children: [
                                  if (p.defaultCode.isNotEmpty)
                                    Text(p.defaultCode, style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary)),
                                  if (p.defaultCode.isNotEmpty)
                                    const SizedBox(width: 12),
                                  Text(p.formattedPrice, style: GoogleFonts.inter(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.w600)),
                                ],
                              ),
                              onTap: () => Navigator.pop(context, p),
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _CustomerPickerDialog extends StatefulWidget {
  final List<Client> clients;
  const _CustomerPickerDialog({required this.clients});

  @override
  State<_CustomerPickerDialog> createState() => _CustomerPickerDialogState();
}

class _CustomerPickerDialogState extends State<_CustomerPickerDialog> {
  final _searchController = TextEditingController();
  late List<Client> _filtered;

  @override
  void initState() {
    super.initState();
    _filtered = widget.clients;
    _searchController.addListener(_filter);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _filter() {
    final q = _searchController.text.toLowerCase();
    setState(() {
      _filtered = q.isEmpty
          ? widget.clients
          : widget.clients.where((c) =>
              c.name.toLowerCase().contains(q) ||
              c.email.toLowerCase().contains(q) ||
              c.companyName.toLowerCase().contains(q)).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520, maxHeight: 600),
        child: Material(
          borderRadius: BorderRadius.circular(18),
          color: AppColors.surface,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text('Seleccionar cliente', style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    hintText: 'Buscar por nombre, email o empresa...',
                    prefixIcon: Icon(Icons.search),
                    isDense: true,
                  ),
                ),
                const SizedBox(height: 12),
                Expanded(
                  child: _filtered.isEmpty
                      ? Center(
                          child: Text('Sin resultados', style: GoogleFonts.inter(color: AppColors.textSecondary)),
                        )
                      : ListView.separated(
                          itemCount: _filtered.length,
                          separatorBuilder: (_, __) => const Divider(height: 1),
                          itemBuilder: (ctx, i) {
                            final c = _filtered[i];
                            return ListTile(
                              leading: CircleAvatar(
                                radius: 16,
                                backgroundColor: AppColors.primary.withValues(alpha: 0.08),
                                child: Text(
                                  c.initials,
                                  style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.primary),
                                ),
                              ),
                              title: Text(c.name, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500)),
                              subtitle: Row(
                                children: [
                                  if (c.email.isNotEmpty)
                                    Flexible(child: Text(c.email, style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary), overflow: TextOverflow.ellipsis)),
                                  if (c.email.isNotEmpty && c.companyName.isNotEmpty)
                                    const Text(' · ', style: TextStyle(color: AppColors.textSecondary)),
                                  if (c.companyName.isNotEmpty)
                                    Flexible(child: Text(c.companyName, style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary), overflow: TextOverflow.ellipsis)),
                                ],
                              ),
                              onTap: () => Navigator.pop(context, c),
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}