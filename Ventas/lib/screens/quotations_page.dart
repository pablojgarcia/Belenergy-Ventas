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
  late Future<List<Map<String, dynamic>>> _itemsFuture;
  List<Map<String, dynamic>> _allItems = [];
  List<Map<String, dynamic>> _filteredItems = [];
  bool _loaded = false;
  String? _selectedTab;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _itemsFuture = _fetchItems();
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

  Future<List<Map<String, dynamic>>> _fetchItems() async {
    final api = context.read<ApiService>();
    final drafts = await api.getDrafts();
    final quotations = await api.getQuotations();
    final merged = <Map<String, dynamic>>[];

    for (final d in drafts) {
      if (d['status'] == 'generated') continue;
      merged.add({
        ...d,
        '_type': 'draft',
        '_sort_date': d['created_at'] as String? ?? '',
      });
    }
    for (final q in quotations) {
      merged.add({
        ...q,
        '_type': 'quotation',
        '_sort_date': q['created_at'] as String? ?? '',
      });
    }
    merged.sort((a, b) => (b['_sort_date'] as String).compareTo(a['_sort_date'] as String));

    if (_selectedTab != null) {
      if (_selectedTab == 'draft') {
        merged.removeWhere((i) => i['_type'] != 'draft');
      } else if (_selectedTab == 'generated') {
        merged.removeWhere((i) => i['_type'] != 'quotation');
      }
    }
    return merged;
  }

  Future<void> _refresh() async {
    setState(() {
      _loaded = false;
      _itemsFuture = _fetchItems();
    });
    await _itemsFuture;
  }

  void _filterItems(String query) {
    _searchQuery = query.toLowerCase();
    setState(() {
      _filteredItems = _allItems.where((o) {
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
            onSelected: (tab) {
              setState(() {
                _selectedTab = tab;
                _loaded = false;
                _itemsFuture = _fetchItems();
              });
            },
            itemBuilder: (_) => [
              const PopupMenuItem(value: null, child: Text('Todos')),
              const PopupMenuItem(value: 'draft', child: Text('Borradores')),
              const PopupMenuItem(value: 'generated', child: Text('Generadas')),
            ],
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _refresh),
        ],
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _itemsFuture,
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
            final items = snapshot.data ?? [];
            _allItems = items;
            _filteredItems = items;
            _loaded = true;
          }

          if (_allItems.isEmpty) {
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
        onChanged: _filterItems,
        decoration: InputDecoration(
          hintText: 'Buscar por cliente...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () => _filterItems(''),
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
                  AppColumn(title: 'Monto', flex: 1),
                  AppColumn(title: 'Tipo', flex: 1),
                  AppColumn(title: 'Estado', flex: 1),
                  AppColumn(title: '', flex: 1),
                ],
                items: _filteredItems,
                cellBuilder: (_, item, col) {
                  final isDraft = item['_type'] == 'draft';
                  final amountTotal = (item['amount_total'] ?? 0.0).toDouble();
                  switch (col) {
                    case 0:
                      return Text(
                        _clientName(item),
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
                        isDraft ? 'Borrador' : 'Cotización',
                        style: TextStyle(
                          fontWeight: FontWeight.w500,
                          color: isDraft ? Colors.orange : AppColors.primary,
                        ),
                      );
                    case 3:
                      return _buildStateChip(isDraft ? (item['status'] as String? ?? 'draft') : 'generated');
                    case 4:
                      return TextButton(
                        onPressed: () => context.push('/quotations/${isDraft ? item['id'] : item['id']}'),
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
      itemCount: _filteredItems.length,
      itemBuilder: (context, i) => _OrderCard(
        item: _filteredItems[i],
        onTap: () => context.push('/quotations/${_filteredItems[i]['id']}'),
      ),
    );
  }

  String _clientName(Map<String, dynamic> item) {
    final name = item['customer_name'] as String?;
    if (name != null && name.isNotEmpty) return name;
    final notes = item['notes'] as String?;
    if (item['_type'] == 'draft') {
      return notes != null && notes.isNotEmpty ? notes : 'Borrador';
    }
    return notes ?? 'Cotización';
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

class _OrderCard extends StatelessWidget {
  final Map<String, dynamic> item;
  final VoidCallback onTap;

  const _OrderCard({required this.item, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isDraft = item['_type'] == 'draft';
    final state = isDraft ? (item['status'] as String? ?? 'draft') : 'generated';
    final amountTotal = (item['amount_total'] ?? 0.0).toDouble();

    final clientName = item['customer_name'] as String? ?? '';
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        onTap: onTap,
        title: Row(
          children: [
            Expanded(
              child: Text(
                clientName.isNotEmpty ? clientName : (isDraft ? 'Borrador' : 'Cotización'),
                style: GoogleFonts.inter(fontWeight: FontWeight.w600),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isDraft ? 'Borrador · \$${amountTotal.toStringAsFixed(2)}' : 'Cotización · \$${amountTotal.toStringAsFixed(2)}',
              style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
            ),
            if (!isDraft && item['odoo_sale_order_name'] != null)
              Text(
                item['odoo_sale_order_name'] as String,
                style: GoogleFonts.inter(fontSize: 11, color: AppColors.textSecondary),
              ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: _stateColor(state).withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            _stateLabel(state),
            style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500, color: _stateColor(state)),
          ),
        ),
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
