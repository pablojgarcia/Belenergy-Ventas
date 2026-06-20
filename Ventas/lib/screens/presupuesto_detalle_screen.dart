import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';

class PresupuestoDetalleScreen extends StatefulWidget {
  final int orderId;

  const PresupuestoDetalleScreen({super.key, required this.orderId});

  @override
  State<PresupuestoDetalleScreen> createState() => _PresupuestoDetalleScreenState();
}

class _PresupuestoDetalleScreenState extends State<PresupuestoDetalleScreen> {
  late Future<Map<String, dynamic>> _orderFuture;

  @override
  void initState() {
    super.initState();
    _orderFuture = _fetchOrder();
  }

  Future<Map<String, dynamic>> _fetchOrder() {
    final api = context.read<ApiService>();
    return api.getOrder(widget.orderId);
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
      body: FutureBuilder<Map<String, dynamic>>(
        future: _orderFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text('Error al cargar presupuesto', style: GoogleFonts.inter(color: Colors.red)),
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
              Text(order['client_name'] ?? '', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
              const SizedBox(height: 16),
              _infoRow('Monto total', Text('\$${(order['amount_total'] ?? 0.0).toStringAsFixed(2)}', style: GoogleFonts.inter(fontWeight: FontWeight.w600))),
              const SizedBox(height: 12),
                _infoRow('Estado', _buildStateChip(order['state'] as String? ?? '')),
                if (order['vendedor_externo'] != null && (order['vendedor_externo'] as String).isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _infoRow('Vendedor externo', Text(order['vendedor_externo'], style: GoogleFonts.inter(fontSize: 14, color: AppColors.textPrimary))),
                ],
              if (order['description'] != null && (order['description'] as String).isNotEmpty) ...[
                const SizedBox(height: 20),
                Text('Descripción', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
                const SizedBox(height: 8),
                Text(order['description'], style: GoogleFonts.inter(fontSize: 15, color: AppColors.textPrimary)),
              ],
            ],
          ),
        ),
        const SizedBox(width: 48),
        Expanded(
          flex: 1,
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppColors.divider),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Detalles', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
                const SizedBox(height: 12),
                Text('ID: ${order['id']}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                const SizedBox(height: 8),
                Text('Fecha: ${order['date_order'] ?? '—'}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                if (order['vendedor_externo'] != null && (order['vendedor_externo'] as String).isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text('Vend. externo: ${order['vendedor_externo']}', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMobileDetail(Map<String, dynamic> order) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(order['client_name'] ?? '', style: GoogleFonts.inter(fontSize: 22, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(height: 8),
        Text('Total: \$${(order['amount_total'] ?? 0.0).toStringAsFixed(2)}',
            style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w600, color: AppColors.primary)),
        const SizedBox(height: 12),
        _infoRow('Estado', _buildStateChip(order['state'] as String? ?? '')),
        if (order['description'] != null && (order['description'] as String).isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(order['description'], style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary)),
        ],
      ],
    );
  }

  Widget _infoRow(String label, Widget value) {
    return Row(
      children: [
        Text('$label: ', style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary)),
        const SizedBox(width: 8),
        value,
      ],
    );
  }

  Widget _buildStateChip(String state) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: _stateColor(state).withOpacity(0.15),
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
      case 'draft': return 'Borrador';
      case 'sent': return 'Enviado';
      case 'sale': return 'Vendido';
      case 'cancel': return 'Cancelado';
      default: return state;
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
