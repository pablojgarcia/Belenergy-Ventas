import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../widgets/app_table.dart';

class QuotationsPage extends StatefulWidget {
  const QuotationsPage({super.key});

  @override
  State<QuotationsPage> createState() => _QuotationsPageState();
}

class _QuotationsPageState extends State<QuotationsPage> {
  late Future<List<Map<String, dynamic>>> _ordersFuture;
  List<Map<String, dynamic>> _allOrders = [];
  List<Map<String, dynamic>> _filteredOrders = [];
  bool _loaded = false;
  String? _selectedState;
  String _searchQuery = '';

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
    setState(() {
      _loaded = false;
      _ordersFuture = _fetchOrders();
    });
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

  void _filterOrders(String query) {
    _searchQuery = query.toLowerCase();
    setState(() {
      _filteredOrders = _allOrders.where((o) {
        final name = (o['client_name'] as String? ?? '').toLowerCase();
        return name.contains(_searchQuery);
      }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Cotizaciones', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
        actions: [
          FilledButton.icon(
            onPressed: () => context.push('/quotations/new'),
            icon: const Icon(Icons.add, size: 20),
            label: const Text('Nueva cotización'),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              textStyle: GoogleFonts.inter(fontWeight: FontWeight.w600),
            ),
          ),
          const SizedBox(width: 8),
          PopupMenuButton<String?>(
            icon: const Icon(Icons.filter_list),
            onSelected: (state) {
              setState(() {
                _selectedState = state;
                _loaded = false;
                _ordersFuture = _fetchOrders();
              });
            },
            itemBuilder: (_) => [
              const PopupMenuItem(value: null, child: Text('Todos')),
              const PopupMenuItem(value: 'draft', child: Text('Creada')),
              const PopupMenuItem(value: 'sent', child: Text('Cotización enviada')),
              const PopupMenuItem(value: 'sale', child: Text('Orden de venta')),
              const PopupMenuItem(value: 'cancel', child: Text('Cancelada')),
            ],
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _refresh),
        ],
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _ordersFuture,
        builder: (context, snapshot) {
          if (!_loaded) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(
                child: Text(
                  'Error al cargar cotizaciones',
                  style: GoogleFonts.inter(color: Colors.red),
                ),
              );
            }
            final orders = snapshot.data ?? [];
            _allOrders = orders;
            _filteredOrders = orders;
            _loaded = true;
          }

          if (_allOrders.isEmpty) {
            return Center(
              child: Text(
                'No hay cotizaciones',
                style: GoogleFonts.inter(color: AppColors.textSecondary),
              ),
            );
          }

          if (context.isDesktop) {
            return _buildDesktopTable();
          }

          return _buildMobileList();
        },
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
      child: TextField(
        onChanged: _filterOrders,
        decoration: InputDecoration(
          hintText: 'Buscar por cliente...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () => _filterOrders(''),
                )
              : null,
          isDense: true,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
      ),
    );
  }

  Widget _buildDesktopTable() {
    return Column(
      children: [
        _buildSearchBar(),
        Expanded(
          child: ClipRect(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
              child: AppTable<Map<String, dynamic>>(
                columns: const [
                  AppColumn(title: 'Cliente', flex: 3),
                  AppColumn(title: 'Monto sin IVA', flex: 1),
                  AppColumn(title: 'IVA', flex: 1),
                  AppColumn(title: 'Monto Total', flex: 1),
                  AppColumn(title: 'Estado', flex: 1),
                  AppColumn(title: '', flex: 1),
                ],
                items: _filteredOrders,
                cellBuilder: (_, order, col) {
                  final amountTotal = (order['amount_total'] ?? 0.0).toDouble();
                  final amountTax = (order['amount_tax'] ?? 0.0).toDouble();
                  final amountGrandTotal = amountTotal + amountTax;
                  switch (col) {
                    case 0:
                      return Text(
                        order['client_name'] as String? ?? '',
                        style: const TextStyle(fontWeight: FontWeight.w500),
                        overflow: TextOverflow.ellipsis,
                      );
                    case 1:
                      return Text(
                        '\$${amountTotal.toStringAsFixed(2)}',
                        style: const TextStyle(fontWeight: FontWeight.w500),
                      );
                    case 2:
                      return Text(
                        '\$${amountTax.toStringAsFixed(2)}',
                        style: TextStyle(fontWeight: FontWeight.w500, color: amountTax > 0 ? null : AppColors.textSecondary),
                      );
                    case 3:
                      return Text(
                        '\$${amountGrandTotal.toStringAsFixed(2)}',
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      );
                    case 4:
                      return _buildStateChip(order['state'] as String? ?? '');
                    case 5:
                      return TextButton(
                        onPressed: () => context.push('/quotations/${order['id']}'),
                        child: const Text('Ver detalle'),
                      );
                    default:
                      return const SizedBox();
                  }
                },
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMobileList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _filteredOrders.length,
      itemBuilder: (context, i) => _OrderCard(
        order: _filteredOrders[i],
        onTap: () => context.push('/quotations/${_filteredOrders[i]['id']}'),
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
    final amountTotal = (order['amount_total'] ?? 0.0).toDouble();
    final amountTax = (order['amount_tax'] ?? 0.0).toDouble();
    final amountGrandTotal = amountTotal + amountTax;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        onTap: onTap,
        title: Text(
          order['client_name'] ?? '',
          style: GoogleFonts.inter(fontWeight: FontWeight.w600),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Row(
              children: [
                Text('Sin IVA: ', style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary)),
                Text('\$${amountTotal.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
                const SizedBox(width: 12),
                Text('IVA: ', style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary)),
                Text('\$${amountTax.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
              ],
            ),
            const SizedBox(height: 2),
            Row(
              children: [
                Text('Total: ', style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                Text('\$${amountGrandTotal.toStringAsFixed(2)}', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.primary)),
              ],
            ),
          ],
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
