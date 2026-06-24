import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';

class QuotationDetailPage extends StatefulWidget {
  final int orderId;

  const QuotationDetailPage({super.key, required this.orderId});

  @override
  State<QuotationDetailPage> createState() => _QuotationDetailPageState();
}

class _QuotationDetailPageState extends State<QuotationDetailPage> {
  late Future<Map<String, dynamic>> _orderFuture;
  late Future<List<Map<String, dynamic>>> _statusesFuture;
  late Future<List<Map<String, dynamic>>> _linesFuture;

  @override
  void initState() {
    super.initState();
    _orderFuture = _fetchOrder();
    _statusesFuture = _fetchStatuses();
    _linesFuture = _fetchLines();
  }

  Future<Map<String, dynamic>> _fetchOrder() {
    final api = context.read<ApiService>();
    return api.getOrder(widget.orderId);
  }

  Future<List<Map<String, dynamic>>> _fetchStatuses() {
    final api = context.read<ApiService>();
    return api.getOrderStatuses(widget.orderId);
  }

  Future<List<Map<String, dynamic>>> _fetchLines() async {
    final api = context.read<ApiService>();
    var lines = await api.getOrderLines(widget.orderId);
    if (lines.isEmpty) {
      try {
        await api.syncOrderLines(widget.orderId);
        lines = await api.getOrderLines(widget.orderId);
      } catch (_) {}
    }
    return lines;
  }

  Future<void> _syncStatus() async {
    final api = context.read<ApiService>();
    try {
      await api.syncOrderStatus(widget.orderId);
      setState(() {
        _orderFuture = _fetchOrder();
        _statusesFuture = _fetchStatuses();
      });
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al sincronizar'), backgroundColor: AppColors.error),
      );
    }
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
        actions: [
          IconButton(icon: const Icon(Icons.sync), onPressed: _syncStatus),
        ],
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _orderFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text('Error al cargar cotización', style: GoogleFonts.inter(color: Colors.red)),
            );
          }
          final order = snapshot.data!;
          final padding = context.isDesktop ? 48.0 : 20.0;

          return SingleChildScrollView(
            padding: EdgeInsets.all(padding),
            child: context.isDesktop
                ? _buildDesktopDetail(order)
                : _buildMobileDetail(order),
          );
        },
      ),
    );
  }

  Widget _buildDesktopDetail(Map<String, dynamic> order) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 2,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(order),
              const SizedBox(height: 24),
              _buildLinesCard(),
              const SizedBox(height: 24),
              _buildTotalsCard(order),
            ],
          ),
        ),
        const SizedBox(width: 24),
        SizedBox(
          width: 320,
          child: Column(
            children: [
              _buildDetailsCard(order),
              const SizedBox(height: 16),
              _buildStatusHistoryCard(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMobileDetail(Map<String, dynamic> order) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildHeader(order),
        const SizedBox(height: 20),
        _buildLinesCard(),
        const SizedBox(height: 16),
        _buildTotalsCard(order),
        const SizedBox(height: 16),
        _buildDetailsCard(order),
        const SizedBox(height: 16),
        _buildStatusHistoryCard(),
      ],
    );
  }

  Widget _card({
    required Widget child,
    double? width,
    EdgeInsetsGeometry? padding,
  }) {
    return Container(
      width: width,
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

  Widget _buildHeader(Map<String, dynamic> order) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              order['client_name'] ?? '',
              style: GoogleFonts.inter(fontSize: 24, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
            ),
            const SizedBox(width: 12),
            _buildStateChip(order['state'] as String? ?? ''),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          'Cotización N° ${order['odoo_id']}',
          style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary),
        ),
        if (order['date_order'] != null)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              _formatDate(order['date_order'] as String),
              style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary),
            ),
          ),
        if (order['description'] != null && (order['description'] as String).isNotEmpty) ...[
          const SizedBox(height: 16),
          _sectionTitle('DESCRIPCIÓN'),
          const SizedBox(height: 8),
          Text(
            order['description'],
            style: GoogleFonts.inter(fontSize: 14, color: AppColors.textPrimary),
          ),
        ],
      ],
    );
  }

  Widget _buildLinesCard() {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _linesFuture,
      builder: (context, snapshot) {
        final lines = snapshot.data ?? [];
        final loading = snapshot.connectionState == ConnectionState.waiting;

        return _card(
          padding: const EdgeInsets.all(0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 12),
                child: _sectionTitle('PRODUCTOS'),
              ),
              if (loading)
                const Padding(
                  padding: EdgeInsets.all(20),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (lines.isEmpty)
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: Text('Sin productos', style: GoogleFonts.inter(color: AppColors.textSecondary)),
                )
              else
                ...lines.asMap().entries.map((entry) {
                  final i = entry.key;
                  final line = entry.value;
                  return _buildLineRow(line, i == lines.length - 1);
                }),
            ],
          ),
        );
      },
    );
  }

  Widget _buildLineRow(Map<String, dynamic> line, bool isLast) {
    final qty = (line['quantity'] as num).toDouble();
    final priceUnit = (line['price_unit'] as num).toDouble();
    final discount = (line['discount'] as num).toDouble();
    final subtotal = (line['subtotal'] as num).toDouble();

    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 12),
      decoration: BoxDecoration(
        border: isLast ? null : Border(bottom: BorderSide(color: AppColors.divider)),
      ),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  line['product_name'] as String? ?? 'Producto',
                  style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                ),
                if (line['description'] != null && (line['description'] as String).isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(
                    line['description'],
                    style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ],
            ),
          ),
          SizedBox(
            width: 60,
            child: Text(
              'x${qty.toStringAsFixed(0)}',
              style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary),
              textAlign: TextAlign.center,
            ),
          ),
          SizedBox(
            width: 90,
            child: Text(
              '\$${priceUnit.toStringAsFixed(2)}',
              style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary),
              textAlign: TextAlign.right,
            ),
          ),
          if (discount > 0)
            SizedBox(
              width: 60,
              child: Text(
                '-${discount.toStringAsFixed(0)}%',
                style: GoogleFonts.inter(fontSize: 12, color: Colors.orange, fontWeight: FontWeight.w600),
                textAlign: TextAlign.center,
              ),
            ),
          SizedBox(
            width: 90,
            child: Text(
              '\$${subtotal.toStringAsFixed(2)}',
              style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTotalsCard(Map<String, dynamic> order) {
    final amount = (order['amount_total'] ?? 0.0) as num;

    return _card(
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                'MONTO CON IVA',
                style: GoogleFonts.inter(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textSecondary,
                  letterSpacing: 0.5,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                '\$${amount.toStringAsFixed(2)}',
                style: GoogleFonts.inter(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDetailsCard(Map<String, dynamic> order) {
    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionTitle('DETALLES'),
          const SizedBox(height: 16),
          _detailRow('Estado', _stateLabel(order['state'] as String? ?? '')),
          const SizedBox(height: 10),
          _detailRow('N° de cotización', '${order['odoo_id']}'),
          const SizedBox(height: 10),
          if (order['date_order'] != null)
            _detailRow('Fecha', _formatDate(order['date_order'] as String)),
          if (order['vendedor_externo'] != null && (order['vendedor_externo'] as String).isNotEmpty) ...[
            const SizedBox(height: 10),
            _detailRow('Vend. externo', order['vendedor_externo'] as String),
          ],
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

  Widget _buildStatusHistoryCard() {
    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionTitle('HISTORIAL DE ESTADOS'),
          const SizedBox(height: 16),
          _buildStatusHistory(),
        ],
      ),
    );
  }

  Widget _buildStatusHistory() {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _statusesFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: Padding(padding: EdgeInsets.all(8), child: CircularProgressIndicator()));
        }
        if (snapshot.hasError || snapshot.data == null || snapshot.data!.isEmpty) {
          return Text('Sin historial', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary));
        }
        final statuses = snapshot.data!;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: statuses.map((s) {
            final status = s['status'] as String? ?? '';
            final changedAt = s['changed_at'] as String? ?? '';
            return Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                children: [
                  _buildStateChip(status),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _formatDate(changedAt),
                      style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        );
      },
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
      case 'creada':
        return 'Creada';
      case 'sent':
      case 'cotizacion_enviada':
        return 'Cotización enviada';
      case 'sale':
      case 'orden_de_venta':
        return 'Orden de venta';
      case 'cancel':
      case 'cancelada':
        return 'Cancelada';
      default:
        return state;
    }
  }

  Color _stateColor(String state) {
    switch (state) {
      case 'draft': return Colors.orange;
      case 'sent': return AppColors.primary;
      case 'sale': return Colors.green;
      case 'cancel': return Colors.red;
      default: return AppColors.textSecondary;
    }
  }
}
