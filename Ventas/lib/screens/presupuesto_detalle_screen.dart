import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

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
              child: Text(
                'Error al cargar presupuesto',
                style: GoogleFonts.inter(color: Colors.red),
              ),
            );
          }
          final order = snapshot.data!;
          return Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  order['client_name'] ?? '',
                  style: GoogleFonts.inter(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Total: \$${(order['amount_total'] ?? 0.0).toStringAsFixed(2)}',
                  style: GoogleFonts.inter(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primary,
                  ),
                ),
                if (order['description'] != null && (order['description'] as String).isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    order['description'],
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
                const SizedBox(height: 16),
                Text(
                  'Estado: ${order['state']}',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
