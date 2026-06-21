import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../models/client_model.dart';
import '../models/product_model.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';

class CrearPresupuestoScreen extends StatefulWidget {
  final Client client;

  const CrearPresupuestoScreen({super.key, required this.client});

  @override
  State<CrearPresupuestoScreen> createState() => _CrearPresupuestoScreenState();
}

class _CrearPresupuestoScreenState extends State<CrearPresupuestoScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final _lineItems = <_LineItem>[];
  bool _loading = false;
  late Client _selectedClient;

  @override
  void initState() {
    super.initState();
    _selectedClient = widget.client;
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    for (final item in _lineItems) {
      item.quantityController.dispose();
      item.discountController.dispose();
    }
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

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_lineItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Agregá al menos un producto')),
      );
      return;
    }

    setState(() => _loading = true);

    final api = context.read<ApiService>();
    try {
      await api.createQuotation({
        'partner_id': _selectedClient.odooId,
        'description': _descriptionController.text,
        'order_line': _lineItems.map((item) => {
          'product_id': item.product.odooId,
          'quantity': item.quantity,
          'price_unit': item.product.listPrice,
          'discount': item.discount,
          'tax_id': [],
        }).toList(),
      });

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: const Text('Presupuesto creado correctamente'), backgroundColor: AppColors.primary),
      );
      context.go('/orders');
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

  void _showCustomerPicker() async {
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
        setState(() => _selectedClient = selected);
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
        title: Text('Crear presupuesto', style: GoogleFonts.inter(fontWeight: FontWeight.w700)),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 0,
        actions: [
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.save_outlined),
            label: const Text('Guardar'),
          ),
          const SizedBox(width: 8),
          FilledButton.icon(
            onPressed: _loading ? null : _submit,
            icon: _loading
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.description_outlined),
            label: const Text('Generar presupuesto'),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: context.isDesktop
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
                hintText: 'Descripción del presupuesto',
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
    return Column(
      children: [
        Container(
          decoration: BoxDecoration(
            color: AppColors.background,
            borderRadius: BorderRadius.circular(8),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          child: Row(
            children: [
              Expanded(flex: 3, child: Text('Producto', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
              SizedBox(width: 100, child: Text('Cantidad', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
              SizedBox(width: 100, child: Text('Precio', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
              SizedBox(width: 100, child: Text('Descuento', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
              SizedBox(width: 100, child: Text('Total', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
              const SizedBox(width: 40),
            ],
          ),
        ),
        ..._lineItems.asMap().entries.map((entry) => _buildProductRow(entry.key, entry.value)),
      ],
    );
  }

  Widget _buildProductRow(int index, _LineItem item) {
    final total = item.quantity * item.product.listPrice * (1 - item.discount / 100);
    return Container(
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.divider.withValues(alpha: 0.3))),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Text(item.product.name, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
          ),
          SizedBox(
            width: 100,
            child: TextFormField(
              controller: item.quantityController,
              decoration: const InputDecoration(isDense: true, contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 6)),
              keyboardType: TextInputType.number,
              validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
            ),
          ),
          SizedBox(
            width: 100,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: Text('\$${item.product.listPrice.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
            ),
          ),
          SizedBox(
            width: 100,
            child: TextFormField(
              controller: item.discountController,
              decoration: const InputDecoration(isDense: true, contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 6)),
              keyboardType: TextInputType.number,
            ),
          ),
          SizedBox(
            width: 100,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: Text('\$${total.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.primary)),
            ),
          ),
          SizedBox(
            width: 40,
            child: IconButton(
              icon: const Icon(Icons.close, size: 16),
              onPressed: () => setState(() => _lineItems.removeAt(index)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTotalsCard() {
    final subtotal = _lineItems.fold<double>(
      0.0,
      (sum, item) => sum + item.quantity * item.product.listPrice * (1 - item.discount / 100),
    );

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            _totalRow('Subtotal', subtotal),
            const SizedBox(height: 6),
            _totalRow('IVA', 0),
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Divider(height: 1),
            ),
            _totalRow('TOTAL', subtotal, big: true),
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
    final c = _selectedClient;
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
                onPressed: _editCustomer,
                icon: const Icon(Icons.edit_outlined, size: 18),
                label: const Text('Editar cliente'),
              ),
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: FilledButton.tonalIcon(
                onPressed: _showCustomerPicker,
                icon: const Icon(Icons.swap_horiz, size: 18),
                label: const Text('Cambiar cliente'),
              ),
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _newCustomer,
                icon: const Icon(Icons.person_add_outlined, size: 18),
                label: const Text('Nuevo cliente'),
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
  final quantityController = TextEditingController(text: '1');
  final discountController = TextEditingController(text: '0');

  _LineItem({required this.product});

  double get quantity => double.tryParse(quantityController.text.replaceAll(',', '.')) ?? 1;
  double get discount => double.tryParse(discountController.text.replaceAll(',', '.')) ?? 0;
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