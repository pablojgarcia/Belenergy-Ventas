import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';

class LeadsPage extends StatefulWidget {
  const LeadsPage({super.key});

  @override
  State<LeadsPage> createState() => _LeadsPageState();
}

class _LeadsPageState extends State<LeadsPage> {
  List<Map<String, dynamic>> _items = [];
  String _selectedStatus = '';
  String _searchQuery = '';
  bool _loading = true;
  String? _error;
  final Set<String> _syncingIds = {};

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (mounted) setState(() { _loading = true; _error = null; });
    final api = context.read<ApiService>();
    try {
      final leads = await api.getLeads(
        status: _selectedStatus.isNotEmpty ? _selectedStatus : null,
      );
      if (mounted) {
        setState(() {
          _items = leads;
          _loading = false;
        });
      }
    } catch (e) {
      debugPrint('[LEADS] error: $e');
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e is DioException
              ? (e.response?.data?['detail']?.toString() ?? 'Error al cargar leads')
              : 'Error de conexión';
        });
      }
    }
  }

  Future<void> _syncLead(String id) async {
    setState(() => _syncingIds.add(id));
    try {
      await context.read<ApiService>().syncLead(id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Lead enviado a Odoo'), backgroundColor: AppColors.success),
        );
        _loadData();
      }
    } catch (e) {
      if (mounted) {
        final msg = e is DioException
            ? (e.response?.data?['detail']?.toString() ?? 'Error al enviar')
            : 'Error de conexión';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg), backgroundColor: AppColors.error),
        );
      }
    } finally {
      if (mounted) setState(() => _syncingIds.remove(id));
    }
  }

  void _filterItems(String query) {
    _searchQuery = query.toLowerCase();
    setState(() {});
  }

  List<Map<String, dynamic>> get _displayItems {
    if (_searchQuery.isEmpty) return _items;
    return _items.where((o) {
      final name = (o['company_name'] as String? ?? '').toLowerCase();
      final contact = (o['contact_name'] as String? ?? '').toLowerCase();
      return name.contains(_searchQuery) || contact.contains(_searchQuery);
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Leads', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
        actions: [
          FilledButton.icon(
            onPressed: () => context.push('/leads/new'),
            icon: const Icon(Icons.add, size: 20),
            label: const Text('Nuevo lead'),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              textStyle: GoogleFonts.inter(fontWeight: FontWeight.w600),
            ),
          ),
          const SizedBox(width: 8),
          PopupMenuButton<String>(
            icon: const Icon(Icons.filter_list),
            onSelected: (status) {
              _selectedStatus = status;
              _loadData();
            },
            itemBuilder: (_) => [
              const PopupMenuItem(value: '', child: Text('Todos')),
              const PopupMenuItem(value: 'pendiente', child: Text('Pendiente')),
              const PopupMenuItem(value: 'aprobado', child: Text('Aprobado')),
              const PopupMenuItem(value: 'rechazado', child: Text('Rechazado')),
              const PopupMenuItem(value: 'sincronizado', child: Text('Sincronizado')),
            ],
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) return const Center(child: CircularProgressIndicator());

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 48, color: AppColors.error),
              const SizedBox(height: 16),
              Text(_error!, style: GoogleFonts.inter(color: AppColors.error), textAlign: TextAlign.center),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: _loadData,
                icon: const Icon(Icons.refresh),
                label: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      );
    }

    if (_displayItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.fiber_new_rounded, size: 64, color: AppColors.textSecondary.withValues(alpha: 0.3)),
            const SizedBox(height: 16),
            Text('No hay leads', style: GoogleFonts.inter(color: AppColors.textSecondary, fontSize: 16)),
            const SizedBox(height: 8),
            Text(_selectedStatus.isNotEmpty ? 'No hay leads en estado ${_stateLabel(_selectedStatus)}' : 'Crea un nuevo lead para empezar',
                style: GoogleFonts.inter(color: AppColors.textSecondary, fontSize: 13)),
          ],
        ),
      );
    }

    return Column(
      children: [
        _buildSearchBar(),
        Expanded(child: _buildDesktopTable()),
      ],
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
      child: TextField(
        onChanged: _filterItems,
        decoration: InputDecoration(
          hintText: 'Buscar por empresa o contacto...',
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
          filled: true,
          fillColor: AppColors.surface,
        ),
      ),
    );
  }

  Widget _buildDesktopTable() {
    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
      itemCount: _displayItems.length + 1,
      itemBuilder: (context, index) {
        if (index == 0) {
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.05),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
              border: Border.all(color: AppColors.divider),
            ),
            child: Row(
              children: [
                Expanded(flex: 3, child: Text('Empresa', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
                Expanded(flex: 2, child: Text('Contacto', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
                Expanded(flex: 1, child: Text('Estado', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
                Expanded(flex: 2, child: Text('', style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12, color: AppColors.textSecondary))),
              ],
            ),
          );
        }
        final item = _displayItems[index - 1];
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            color: index.isEven ? AppColors.surface : AppColors.background,
            border: Border.all(color: AppColors.divider),
          ),
          child: InkWell(
            onTap: () => context.push('/leads/${item['id']}'),
            child: Row(
              children: [
                Expanded(flex: 3, child: Text(item['company_name'] ?? '', style: GoogleFonts.inter(fontWeight: FontWeight.w500, fontSize: 13), overflow: TextOverflow.ellipsis)),
                Expanded(flex: 2, child: Text(item['contact_name'] ?? '', style: GoogleFonts.inter(fontSize: 13), overflow: TextOverflow.ellipsis)),
                Expanded(flex: 1, child: _buildStateChip(item['status'] as String? ?? 'pendiente')),
                Expanded(
                  flex: 2,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(onPressed: () => context.push('/leads/${item['id']}'), child: const Text('Ver')),
                      if (item['status'] == 'pendiente' || item['status'] == 'aprobado')
                        _syncingIds.contains(item['id'])
                            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                            : TextButton(
                                onPressed: () => _syncLead(item['id']),
                                child: const Text('Enviar'),
                              ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStateChip(String state) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: _stateColor(state).withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        _stateLabel(state),
        style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w500, color: _stateColor(state)),
      ),
    );
  }

  String _stateLabel(String state) {
    switch (state) {
      case 'pendiente': return 'Pendiente';
      case 'aprobado': return 'Aprobado';
      case 'rechazado': return 'Rechazado';
      case 'sincronizado': return 'Sincronizado';
      default: return state;
    }
  }

  Color _stateColor(String state) {
    switch (state) {
      case 'pendiente': return Colors.orange;
      case 'aprobado': return Colors.blue;
      case 'rechazado': return Colors.red;
      case 'sincronizado': return Colors.green;
      default: return AppColors.textSecondary;
    }
  }
}
