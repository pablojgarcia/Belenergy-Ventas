import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

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
  }

  Future<List<Map<String, dynamic>>> _fetchOrders() {
    final api = context.read<ApiService>();
    return api.getOrders(state: _selectedState);
  }

  void _refresh() {
    setState(() => _ordersFuture = _fetchOrders());
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
              PopupMenuItem(value: 'draft', child: const Text('Borrador')),
              PopupMenuItem(value: 'sent', child: const Text('Enviado')),
              PopupMenuItem(value: 'sale', child: const Text('Vendido')),
              PopupMenuItem(value: 'cancel', child: const Text('Cancelado')),
            ],
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _refresh),
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
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: orders.length,
            itemBuilder: (context, i) => _OrderCard(
              order: orders[i],
              onTap: () => context.push('/orders/${orders[i]['id']}'),
            ),
          );
        },
      ),
    );
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
          style: GoogleFonts.inter(
            color: AppColors.textSecondary,
            fontSize: 13,
          ),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: stateColor.withOpacity(0.15),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            stateLabel,
            style: GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: stateColor,
            ),
          ),
        ),
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
