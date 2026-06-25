import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../utils/download.dart' as download;

class QuotationDetailPage extends StatefulWidget {
  final String itemId;

  const QuotationDetailPage({super.key, required this.itemId});

  @override
  State<QuotationDetailPage> createState() => _QuotationDetailPageState();
}

class _QuotationDetailPageState extends State<QuotationDetailPage> {
  Map<String, dynamic>? _item;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final api = context.read<ApiService>();
    final draft = await api.getDraft(widget.itemId);
    if (draft != null && mounted) {
      setState(() {
        _item = draft;
        _item!['_type'] = 'draft';
        _loading = false;
      });
      return;
    }
    final quotation = await api.getQuotation(widget.itemId);
    if (quotation != null && mounted) {
      setState(() {
        _item = quotation;
        _item!['_type'] = 'quotation';
        _loading = false;
      });
      return;
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Presupuesto', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _item == null
              ? Center(child: Text('No encontrado', style: GoogleFonts.inter(color: Colors.red)))
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    final item = _item!;
    final isDraft = item['_type'] == 'draft';
    final padding = context.isDesktop ? 48.0 : 20.0;

    return SingleChildScrollView(
      padding: EdgeInsets.all(padding),
      child: context.isDesktop
          ? _buildDesktopDetail(item, isDraft)
          : _buildMobileDetail(item, isDraft),
    );
  }

  Widget _buildDesktopDetail(Map<String, dynamic> item, bool isDraft) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 2,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(item, isDraft),
              const SizedBox(height: 24),
              _buildLinesCard(item),
              const SizedBox(height: 24),
              _buildTotalsCard(item, isDraft),
            ],
          ),
        ),
        const SizedBox(width: 24),
        SizedBox(
          width: 320,
          child: _buildDetailsCard(item, isDraft),
        ),
      ],
    );
  }

  Widget _buildMobileDetail(Map<String, dynamic> item, bool isDraft) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildHeader(item, isDraft),
        const SizedBox(height: 20),
        _buildLinesCard(item),
        const SizedBox(height: 16),
        _buildTotalsCard(item, isDraft),
        const SizedBox(height: 16),
        _buildDetailsCard(item, isDraft),
      ],
    );
  }

  Widget _card({required Widget child, EdgeInsetsGeometry? padding}) {
    return Container(
      padding: padding ?? const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.divider),
      ),
      child: child,
    );
  }

  Widget _sectionTitle(String title) {
    return Text(
      title,
      style: GoogleFonts.inter(
        fontSize: 13,
        fontWeight: FontWeight.w600,
        color: AppColors.textSecondary,
        letterSpacing: 0.5,
      ),
    );
  }

  bool _downloadingPdf = false;
  bool _generating = false;

  Future<void> _generate() async {
    setState(() => _generating = true);
    final api = context.read<ApiService>();
    try {
      await api.generateQuotation(widget.itemId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cotización generada correctamente')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al generar: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _generating = false);
        _load();
      }
    }
  }

  Future<void> _downloadPdf() async {
    setState(() => _downloadingPdf = true);
    final api = context.read<ApiService>();
    try {
      final bytes = await api.downloadPdf(widget.itemId);
      final name = 'cotizacion_${widget.itemId.substring(0, 8)}.pdf';
      download.saveBytes(bytes, name);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('PDF descargado: $name')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al descargar PDF: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _downloadingPdf = false);
    }
  }

  Widget _buildHeader(Map<String, dynamic> item, bool isDraft) {
    final status = isDraft ? (item['status'] as String? ?? 'draft') : 'generated';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              isDraft ? 'Borrador' : 'Cotización',
              style: GoogleFonts.inter(fontSize: 24, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
            ),
            const SizedBox(width: 12),
            _buildStateChip(status),
            const Spacer(),
            if (isDraft && item['status'] != 'failed') ...[
              OutlinedButton.icon(
                icon: const Icon(Icons.edit, size: 18),
                label: const Text('Editar'),
                onPressed: () => context.push('/quotations/${widget.itemId}/edit'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.primary,
                ),
              ),
              const SizedBox(width: 8),
              _generating
                  ? const SizedBox(
                      width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : FilledButton.icon(
                      icon: const Icon(Icons.rocket_launch, size: 18),
                      label: const Text('Generar'),
                      onPressed: _generate,
                      style: FilledButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                      ),
                    ),
            ] else if (isDraft && item['status'] == 'failed')
              FilledButton.icon(
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Reintentar'),
                onPressed: _generating ? null : _generate,
                style: FilledButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
              )
            else
              _downloadingPdf
                  ? const SizedBox(
                      width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : IconButton(
                      icon: Icon(Icons.download, color: AppColors.primary),
                      tooltip: 'Descargar PDF',
                      onPressed: _downloadPdf,
                    ),
          ],
        ),
        const SizedBox(height: 6),
        if (!isDraft) ...[
          Text(
            'N° Interno: ${item['odoo_sale_order_name'] ?? item['odoo_sale_order_id']}',
            style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary),
          ),
        ],
        if (item['created_at'] != null)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              _formatDate(item['created_at'] as String),
              style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary),
            ),
          ),
        if (item['notes'] != null && (item['notes'] as String).isNotEmpty) ...[
          const SizedBox(height: 16),
          _sectionTitle('NOTAS'),
          const SizedBox(height: 8),
          Text(
            item['notes'],
            style: GoogleFonts.inter(fontSize: 14, color: AppColors.textPrimary),
          ),
        ],
      ],
    );
  }

  double _calcSubtotal(Map<String, dynamic> line) {
    final qty = (line['quantity'] as num).toDouble();
    final priceUnit = (line['unit_price'] as num?)?.toDouble() ?? (line['price_unit'] as num?)?.toDouble() ?? 0.0;
    final discount = (line['discount'] as num).toDouble();
    return qty * priceUnit * (1 - discount / 100);
  }

  double _calcTax(Map<String, dynamic> line) {
    final taxRate = (line['tax_rate'] as num?)?.toDouble() ?? 0.0;
    return _calcSubtotal(line) * taxRate / 100;
  }

  Widget _buildLinesCard(Map<String, dynamic> item) {
    final lines = item['lines'] as List<dynamic>? ?? [];

    return _card(
      padding: const EdgeInsets.all(0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 20, 20, 12),
            child: _sectionTitle('PRODUCTOS'),
          ),
          if (lines.isEmpty)
            Padding(
              padding: const EdgeInsets.all(20),
              child: Text('Sin productos', style: GoogleFonts.inter(color: AppColors.textSecondary)),
            )
          else
            LayoutBuilder(builder: (context, constraints) {
              final isWide = constraints.maxWidth > 650;
              final content = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _tableHeader(isWide),
                  ...lines.asMap().entries.map((entry) {
                    final line = entry.value as Map<String, dynamic>;
                    return _buildLineRow(line, entry.key == lines.length - 1, isWide);
                  }),
                ],
              );
              if (isWide) return Padding(padding: const EdgeInsets.fromLTRB(20, 0, 20, 0), child: content);
              return SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 0),
                child: content,
              );
            }),
        ],
      ),
    );
  }

  Widget _tableHeader(bool isWide) {
    if (isWide) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: Row(
          children: const [
            Expanded(flex: 3, child: Text('Producto', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Cantidad', textAlign: TextAlign.center, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Precio Unit.', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Dto %', textAlign: TextAlign.center, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Subtotal', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('IVA', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
            Expanded(flex: 1, child: Text('Total', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
          ],
        ),
      );
    }
    return Row(
      children: const [
        SizedBox(width: 160, child: Text('Producto', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
        SizedBox(width: 80, child: Text('Cantidad', textAlign: TextAlign.center, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
        SizedBox(width: 90, child: Text('Precio Unit.', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
        SizedBox(width: 60, child: Text('Dto %', textAlign: TextAlign.center, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
        SizedBox(width: 90, child: Text('Subtotal', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
        SizedBox(width: 90, child: Text('IVA', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
        SizedBox(width: 90, child: Text('Total', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary))),
      ],
    );
  }

  Widget _buildLineRow(Map<String, dynamic> line, bool isLast, bool isWide) {
    final qty = (line['quantity'] as num).toDouble();
    final priceUnit = (line['unit_price'] as num?)?.toDouble() ?? (line['price_unit'] as num?)?.toDouble() ?? 0.0;
    final discount = (line['discount'] as num).toDouble();
    final subtotal = _calcSubtotal(line);
    final tax = _calcTax(line);
    final total = subtotal + tax;
    final productName = line['product_name'] as String? ?? 'Producto #${line['product_id']}';
    final qtyText = '${qty.toStringAsFixed(0)}';
    final puText = '\$${priceUnit.toStringAsFixed(2)}';
    final dtoText = discount > 0 ? '-${discount.toStringAsFixed(0)}%' : '—';
    final subText = '\$${subtotal.toStringAsFixed(2)}';
    final ivaText = tax > 0 ? '\$${tax.toStringAsFixed(2)}' : '—';
    final totalText = '\$${total.toStringAsFixed(2)}';

    if (isWide) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          border: isLast ? null : Border(bottom: BorderSide(color: AppColors.divider)),
        ),
        child: Row(
          children: [
            Expanded(flex: 3, child: Text(productName, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
            Expanded(flex: 1, child: Text(qtyText, textAlign: TextAlign.center, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
            Expanded(flex: 1, child: Text(puText, textAlign: TextAlign.right, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
            Expanded(flex: 1, child: Text(dtoText, textAlign: TextAlign.center, style: GoogleFonts.inter(fontSize: 13, color: discount > 0 ? Colors.orange : AppColors.textSecondary))),
            Expanded(flex: 1, child: Text(subText, textAlign: TextAlign.right, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
            Expanded(flex: 1, child: Text(ivaText, textAlign: TextAlign.right, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
            Expanded(flex: 1, child: Text(totalText, textAlign: TextAlign.right, style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.primary))),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: isLast ? null : Border(bottom: BorderSide(color: AppColors.divider)),
      ),
      child: Row(
        children: [
          SizedBox(width: 160, child: Text(productName, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
          SizedBox(width: 80, child: Text(qtyText, textAlign: TextAlign.center, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
          SizedBox(width: 90, child: Text(puText, textAlign: TextAlign.right, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
          SizedBox(width: 60, child: Text(dtoText, textAlign: TextAlign.center, style: GoogleFonts.inter(fontSize: 13, color: discount > 0 ? Colors.orange : AppColors.textSecondary))),
          SizedBox(width: 90, child: Text(subText, textAlign: TextAlign.right, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
          SizedBox(width: 90, child: Text(ivaText, textAlign: TextAlign.right, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary))),
          SizedBox(width: 90, child: Text(totalText, textAlign: TextAlign.right, style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.primary))),
        ],
      ),
    );
  }

  Widget _buildTotalsCard(Map<String, dynamic> item, bool isDraft) {
    final lines = item['lines'] as List<dynamic>? ?? [];
    final subtotal = lines.fold<double>(0.0, (s, l) => s + _calcSubtotal(l as Map<String, dynamic>));
    final iva = lines.fold<double>(0.0, (s, l) => s + _calcTax(l as Map<String, dynamic>));
    final total = subtotal + iva;

    return _card(
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              _totalRow('Subtotal', subtotal),
              const SizedBox(height: 4),
              _totalRow('IVA', iva),
              const SizedBox(height: 6),
              Text(
                'TOTAL',
                style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textSecondary, letterSpacing: 0.5),
              ),
              const SizedBox(height: 4),
              Text(
                '\$${total.toStringAsFixed(2)}',
                style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.w800, color: AppColors.primary),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _totalRow(String label, double amount) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text('$label:  ', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
        Text('\$${amount.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
      ],
    );
  }

  Widget _buildDetailsCard(Map<String, dynamic> item, bool isDraft) {
    final status = isDraft ? (item['status'] as String? ?? 'draft') : 'generated';

    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionTitle('DETALLES'),
          const SizedBox(height: 16),
          _detailRow('Estado', _stateLabel(status)),
          const SizedBox(height: 10),
          _detailRow('Tipo', isDraft ? 'Borrador' : 'Cotización'),
          const SizedBox(height: 10),
          if (!isDraft) ...[
            _detailRow('N° Odoo', '${item['odoo_sale_order_name'] ?? item['odoo_sale_order_id']}'),
            const SizedBox(height: 10),
          ],
          if (item['created_at'] != null)
            _detailRow('Fecha', _formatDate(item['created_at'] as String)),
        ],
      ),
    );
  }

  Widget _detailRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        SizedBox(
          width: 120,
          child: Text(label, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
        ),
        Expanded(
          child: Text(value, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
        ),
      ],
    );
  }

  String _formatDate(String isoDate) {
    try {
      final dt = DateTime.parse(isoDate);
      final day = dt.day.toString().padLeft(2, '0');
      final month = dt.month.toString().padLeft(2, '0');
      final year = dt.year;
      final hour = dt.hour.toString().padLeft(2, '0');
      final minute = dt.minute.toString().padLeft(2, '0');
      return '$day/$month/$year $hour:$minute';
    } catch (_) {
      return isoDate;
    }
  }

  Widget _buildStateChip(String state) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: _stateColor(state).withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        _stateLabel(state),
        style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500, color: _stateColor(state)),
      ),
    );
  }

  String _stateLabel(String state) {
    switch (state) {
      case 'draft':
        return 'Borrador';
      case 'generated':
        return 'Generada';
      case 'failed':
        return 'Error';
      default:
        return state;
    }
  }

  Color _stateColor(String state) {
    switch (state) {
      case 'draft':
        return Colors.orange;
      case 'generated':
        return Colors.green;
      case 'failed':
        return Colors.red;
      default:
        return AppColors.textSecondary;
    }
  }
}
