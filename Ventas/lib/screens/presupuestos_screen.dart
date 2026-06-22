import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';

class PresupuestosScreen extends StatefulWidget {
  const PresupuestosScreen({super.key});

  @override
  State<PresupuestosScreen> createState() => _PresupuestosScreenState();
}

class _PresupuestosScreenState extends State<PresupuestosScreen> {
  late Future<List<Map<String, dynamic>>> _ordersFuture;
  String? _selectedState;

  @override
  void initState() {
    super.initState();
    _ordersFuture = _fetchOrders();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<ApiService>().ordersRefreshNotifier.addListener(_onRefresh);
      }
    });
  }

  @override
  void dispose() {
    try {
      context.read<ApiService>().ordersRefreshNotifier.removeListener(_onRefresh);
    } catch (_) {}
    super.dispose();
  }

  void _onRefresh() {
    _refresh();
  }

  Future<List<Map<String, dynamic>>> _fetchOrders() {
    final api = context.read<ApiService>();
    return api.getOrders(state: _selectedState);
  }

  Future<void> _refresh() async {
    setState(() => _ordersFuture = _fetchOrders());
    await _ordersFuture;
  }

  Future<void> _syncAllStatuses() async {
    final api = context.read<ApiService>();
    try {
      final data = await api.getOrders();
      for (final order in data) {
        try {
          await api.syncOrderStatus(order['id'] as int);
        } catch (_) {}
      }
      await _refresh();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Estados sincronizados')),
      );
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
        title: Text('Presupuestos', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
        actions: [
          PopupMenuButton<String?>(
            icon: const Icon(Icons.filter_list),
            onSelected: (state) {
              setState(() {
                _selectedState = state;
                _ordersFuture = _fetchOrders();
              });
            },
              itemBuilder: (_) => [
                PopupMenuItem(value: null, child: const Text('Todos')),
                PopupMenuItem(value: 'draft', child: const Text('Creada')),
                PopupMenuItem(value: 'sent', child: const Text('Cotización enviada')),
                PopupMenuItem(value: 'sale', child: const Text('Orden de venta')),
                PopupMenuItem(value: 'cancel', child: const Text('Cancelada')),
              ],
          ),
          IconButton(icon: const Icon(Icons.sync), onPressed: _syncAllStatuses),
        ],
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _ordersFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text(
                'Error al cargar presupuestos',
                style: GoogleFonts.inter(color: Colors.red),
              ),
            );
          }
          final orders = snapshot.data ?? [];
          if (orders.isEmpty) {
            return Center(
              child: Text(
                'No hay presupuestos',
                style: GoogleFonts.inter(color: AppColors.textSecondary),
              ),
            );
          }

          if (context.isDesktop) {
            return _buildDesktopTable(orders);
          }

          return _buildMobileList(orders);
        },
      ),
    );
  }

  Widget _buildDesktopTable(List<Map<String, dynamic>> orders) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
      child: DataTable(
        headingRowColor: WidgetStateProperty.all(AppColors.background),
        columnSpacing: 24,
        columns: const [
          DataColumn(label: Text('Cliente', style: TextStyle(fontWeight: FontWeight.w600))),
          DataColumn(label: Text('Monto', style: TextStyle(fontWeight: FontWeight.w600))),
          DataColumn(label: Text('Estado', style: TextStyle(fontWeight: FontWeight.w600))),
          DataColumn(label: Text('', style: TextStyle(fontWeight: FontWeight.w600))),
        ],
        rows: orders.map((o) {
          final state = o['state'] as String? ?? '';
          return DataRow(cells: [
            DataCell(Text(o['client_name'] ?? '', style: const TextStyle(fontWeight: FontWeight.w500))),
            DataCell(Text('\$${(o['amount_total'] ?? 0.0).toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.w600))),
            DataCell(_buildStateChip(state)),
            DataCell(
              TextButton(
                onPressed: () => context.push('/orders/${o['id']}'),
                child: const Text('Ver detalle'),
              ),
            ),
          ]);
        }).toList(),
      ),
    );
  }

  Widget _buildMobileList(List<Map<String, dynamic>> orders) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: orders.length,
      itemBuilder: (context, i) => _OrderCard(
        order: orders[i],
        onTap: () => context.push('/orders/${orders[i]['id']}'),
      ),
    );
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
      case 'draft':
      case 'creada':
        return Colors.orange;
      case 'sent':
      case 'cotizacion_enviada':
        return AppColors.primary;
      case 'sale':
      case 'orden_de_venta':
        return Colors.green;
      case 'cancel':
      case 'cancelada':
        return Colors.red;
      default:
        return AppColors.textSecondary;
    }
  }
}

class _OrderCard extends StatelessWidget {
  final Map<String, dynamic> order;
  final VoidCallback onTap;

  const _OrderCard({required this.order, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final state = order['state'] as String? ?? '';
    final stateLabel = _stateLabel(state);
    final stateColor = _stateColor(state);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        onTap: onTap,
        title: Text(
          order['client_name'] ?? '',
          style: GoogleFonts.inter(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          '\$${(order['amount_total'] ?? 0.0).toStringAsFixed(2)}',
          style: GoogleFonts.inter(color: AppColors.textSecondary, fontSize: 13),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: stateColor.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            stateLabel,
            style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500, color: stateColor),
          ),
        ),
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
      case 'draft':
      case 'creada':
        return Colors.orange;
      case 'sent':
      case 'cotizacion_enviada':
        return AppColors.primary;
      case 'sale':
      case 'orden_de_venta':
        return Colors.green;
      case 'cancel':
      case 'cancelada':
        return Colors.red;
      default:
        return AppColors.textSecondary;
    }
  }
}
