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
        builder: (ctx) => _ProductPicker(products: products),
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
        'partner_id': widget.client.odooId,
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

  @override
  Widget build(BuildContext context) {
    final content = _buildForm();
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Crear presupuesto', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
      ),
      body: context.isDesktop
          ? Padding(
              padding: const EdgeInsets.all(24),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(flex: 2, child: content),
                  const SizedBox(width: 24),
                  Expanded(
                    flex: 1,
                    child: _buildClientCard(),
                  ),
                ],
              ),
            )
          : content,
    );
  }

  Widget _buildClientCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Cliente', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
          const SizedBox(height: 8),
          Text(widget.client.name, style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700)),
          if (widget.client.company.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(widget.client.company, style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary)),
          ],
          if (widget.client.email.isNotEmpty) ...[
            const SizedBox(height: 12),
            Row(children: [const Icon(Icons.email_outlined, size: 16, color: AppColors.textSecondary), const SizedBox(width: 8), Text(widget.client.email, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary))]),
          ],
          if (widget.client.phone.isNotEmpty) ...[
            const SizedBox(height: 8),
            Row(children: [const Icon(Icons.phone_outlined, size: 16, color: AppColors.textSecondary), const SizedBox(width: 8), Text(widget.client.phone, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary))]),
          ],
          if (widget.client.address.isNotEmpty) ...[
            const SizedBox(height: 8),
            Row(children: [const Icon(Icons.location_on_outlined, size: 16, color: AppColors.textSecondary), const SizedBox(width: 8), Expanded(child: Text(widget.client.address, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)))]),
          ],
        ],
      ),
    );
  }

  Widget _buildForm() {
    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          if (!context.isDesktop) ...[
            Text(widget.client.name, style: GoogleFonts.inter(fontSize: 22, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
            Text(widget.client.company, style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary)),
            const SizedBox(height: 24),
          ],
          TextFormField(
            controller: _descriptionController,
            decoration: const InputDecoration(
              labelText: 'Descripción',
              hintText: 'Ej. instalación solar residencial',
            ),
            maxLines: 2,
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Productos', style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
              TextButton.icon(
                onPressed: _addProduct,
                icon: const Icon(Icons.add),
                label: const Text('Agregar'),
              ),
            ],
          ),
          if (_lineItems.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 20),
              child: Center(
                child: Text('No hay productos agregados', style: GoogleFonts.inter(color: AppColors.textSecondary)),
              ),
            ),
          ..._lineItems.asMap().entries.map((entry) =>
            _ProductLineCard(index: entry.key, item: entry.value, onRemove: () => setState(() => _lineItems.removeAt(entry.key))),
          ),
          const SizedBox(height: 20),
          _buildTotal(),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: _loading ? null : _submit,
            child: _loading
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Generar presupuesto'),
          ),
        ],
      ),
    );
  }

  Widget _buildTotal() {
    final total = _lineItems.fold<double>(
      0.0,
      (sum, item) => sum + item.quantity * item.product.listPrice * (1 - item.discount / 100),
    );
    return Row(
      children: [
        Text('Total: ', style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
        Text('\$${total.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.primary)),
      ],
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

class _ProductLineCard extends StatelessWidget {
  final int index;
  final _LineItem item;
  final VoidCallback onRemove;

  const _ProductLineCard({required this.index, required this.item, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(item.product.name, style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14)),
                ),
                IconButton(icon: const Icon(Icons.close, size: 18), onPressed: onRemove),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: item.quantityController,
                    decoration: const InputDecoration(labelText: 'Cantidad', isDense: true),
                    keyboardType: TextInputType.number,
                    validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text('Precio: \$${item.product.listPrice.toStringAsFixed(2)}',
                      style: GoogleFonts.inter(color: AppColors.textSecondary, fontSize: 13)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: item.discountController,
              decoration: const InputDecoration(labelText: 'Descuento (%)', isDense: true),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
      ),
    );
  }
}

class _ProductPicker extends StatelessWidget {
  final List<Product> products;
  const _ProductPicker({required this.products});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Seleccionar producto', style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            SizedBox(
              height: 300,
              child: ListView.separated(
                itemCount: products.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (ctx, i) {
                  final p = products[i];
                  return ListTile(
                    title: Text(p.name, style: GoogleFonts.inter(fontSize: 14)),
                    subtitle: Text('\$${p.listPrice.toStringAsFixed(2)}',
                        style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary)),
                    onTap: () => Navigator.pop(context, p),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
