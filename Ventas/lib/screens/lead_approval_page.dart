import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../widgets/app_table.dart';

class LeadApprovalPage extends StatefulWidget {
  const LeadApprovalPage({super.key});

  @override
  State<LeadApprovalPage> createState() => _LeadApprovalPageState();
}

class _LeadApprovalPageState extends State<LeadApprovalPage> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadPendingLeads();
  }

  Future<void> _loadPendingLeads() async {
    if (mounted) setState(() => _loading = true);
    final api = context.read<ApiService>();
    try {
      final leads = await api.getLeads(status: 'pendiente');
      if (mounted) setState(() { _items = leads; _loading = false; });
    } catch (e) {
      debugPrint('[LEAD_APPROVAL] error: $e');
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _approveLead(String id) async {
    try {
      await context.read<ApiService>().approveLead(id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Lead aprobado'), backgroundColor: AppColors.success),
        );
        _loadPendingLeads();
      }
    } catch (e) {
      if (mounted) {
        final msg = e is DioException
            ? (e.response?.data?['detail'] ?? 'Error al aprobar')
            : 'Error al aprobar';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg), backgroundColor: AppColors.error),
        );
      }
    }
  }

  Future<void> _rejectLead(String id) async {
    final reasonController = TextEditingController();
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Rechazar lead', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
        content: TextField(
          controller: reasonController,
          decoration: const InputDecoration(
            labelText: 'Motivo de rechazo',
            hintText: 'Ej: Cliente ya existe',
          ),
          maxLines: 3,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () {
              final reason = reasonController.text.trim();
              if (reason.isEmpty) return;
              Navigator.pop(ctx, reason);
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            child: const Text('Rechazar'),
          ),
        ],
      ),
    );

    if (result != null) {
      try {
        await context.read<ApiService>().rejectLead(id, result);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Lead rechazado')),
          );
          _loadPendingLeads();
        }
      } catch (e) {
        if (mounted) {
          final msg = e is DioException
              ? (e.response?.data?['detail'] ?? 'Error al rechazar')
              : 'Error al rechazar';
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(msg), backgroundColor: AppColors.error),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Aprobar leads', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadPendingLeads),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _items.isEmpty
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.check_circle, size: 64, color: AppColors.success.withValues(alpha: 0.5)),
                      const SizedBox(height: 16),
                      Text('No hay leads pendientes',
                          style: GoogleFonts.inter(color: AppColors.textSecondary, fontSize: 16)),
                    ],
                  ),
                )
              : context.isDesktop
                  ? _buildDesktopTable()
                  : _buildMobileList(),
    );
  }

  Widget _buildDesktopTable() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: AppTable<Map<String, dynamic>>(
        columns: const [
          AppColumn(title: 'Empresa', flex: 3),
          AppColumn(title: 'Contacto', flex: 2),
          AppColumn(title: 'Email', flex: 2),
          AppColumn(title: '', flex: 2),
        ],
        items: _items,
        cellBuilder: (_, item, col) {
          switch (col) {
            case 0:
              return Text(
                item['company_name'] ?? '',
                style: const TextStyle(fontWeight: FontWeight.w500),
                overflow: TextOverflow.ellipsis,
              );
            case 1:
              return Text(item['contact_name'] ?? '', overflow: TextOverflow.ellipsis);
            case 2:
              return Text(item['email'] ?? '', overflow: TextOverflow.ellipsis);
            case 3:
              return Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.check_circle, color: AppColors.success),
                    tooltip: 'Aprobar',
                    onPressed: () => _approveLead(item['id']),
                  ),
                  IconButton(
                    icon: const Icon(Icons.cancel, color: AppColors.error),
                    tooltip: 'Rechazar',
                    onPressed: () => _rejectLead(item['id']),
                  ),
                ],
              );
            default:
              return const SizedBox();
          }
        },
      ),
    );
  }

  Widget _buildMobileList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _items.length,
      itemBuilder: (context, i) {
        final item = _items[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['company_name'] ?? '',
                    style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 16)),
                if (item['contact_name'] != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(item['contact_name'],
                        style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                  ),
                if (item['email'] != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Text(item['email'],
                        style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                  ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _approveLead(item['id']),
                        icon: const Icon(Icons.check_circle, size: 18),
                        label: const Text('Aprobar'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: AppColors.success,
                          side: BorderSide(color: AppColors.success.withValues(alpha: 0.3)),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _rejectLead(item['id']),
                        icon: const Icon(Icons.cancel, size: 18),
                        label: const Text('Rechazar'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: AppColors.error,
                          side: BorderSide(color: AppColors.error.withValues(alpha: 0.3)),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
