import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

class LeadDetailPage extends StatefulWidget {
  final String leadId;

  const LeadDetailPage({super.key, required this.leadId});

  @override
  State<LeadDetailPage> createState() => _LeadDetailPageState();
}

class _LeadDetailPageState extends State<LeadDetailPage> {
  Map<String, dynamic>? _lead;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadLead();
  }

  Future<void> _loadLead() async {
    final api = context.read<ApiService>();
    try {
      final lead = await api.getLead(widget.leadId);
      if (mounted) setState(() { _lead = lead; _loading = false; });
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error al cargar el lead')),
        );
      }
    }
  }

  Future<void> _deleteLead() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Eliminar lead', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
        content: Text('¿Estás seguro de eliminar este lead?', style: GoogleFonts.inter()),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await context.read<ApiService>().deleteLead(widget.leadId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Lead eliminado'), backgroundColor: AppColors.success),
          );
          context.pop();
        }
      } catch (e) {
        if (mounted) {
          final msg = e is DioException
              ? (e.response?.data?['detail'] ?? 'Error al eliminar')
              : 'Error al eliminar';
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(msg), backgroundColor: AppColors.error),
          );
        }
      }
    }
  }

  bool _refreshing = false;
  bool _creatingQuotation = false;

  Future<void> _createQuotation() async {
    setState(() => _creatingQuotation = true);
    try {
      final result = await context.read<ApiService>().createDraftFromLead(widget.leadId);
      final customerId = result['customer_id'];
      if (mounted && customerId != null) {
        context.go('/quotations/new?customer=$customerId');
      }
    } catch (e) {
      if (mounted) {
        final msg = e is DioException
            ? (e.response?.data?['detail']?.toString() ?? 'Error al crear la cotización')
            : 'Error de conexión';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg), backgroundColor: AppColors.error),
        );
      }
    } finally {
      if (mounted) setState(() => _creatingQuotation = false);
    }
  }

  Future<void> _refreshLead() async {
    setState(() => _refreshing = true);
    try {
      final updated = await context.read<ApiService>().refreshLead(widget.leadId);
      if (mounted) {
        setState(() {
          _lead = updated;
          _refreshing = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Lead actualizado desde CRM'), backgroundColor: AppColors.success),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _refreshing = false);
        final msg = e is DioException
            ? (e.response?.data?['detail']?.toString() ?? 'Error al actualizar')
            : 'Error de conexión';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg), backgroundColor: AppColors.error),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Detalle del lead', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
        actions: [
          if (_lead != null && _lead!['odoo_crm_lead_id'] != null)
            _refreshing
                ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2))
                : IconButton(
                    icon: const Icon(Icons.sync),
                    tooltip: 'Actualizar desde CRM',
                    onPressed: _refreshLead,
                  ),
          if (_lead != null && _lead!['status'] == 'aprobado')
            _creatingQuotation
                ? const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 12),
                    child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
                  )
                : IconButton(
                    icon: const Icon(Icons.request_quote),
                    tooltip: 'Crear cotización',
                    onPressed: _createQuotation,
                  ),
          if (_lead != null && _lead!['status'] == 'pendiente') ...[
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => context.push('/leads/${widget.leadId}/edit'),
            ),
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: _deleteLead,
            ),
          ],
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _lead == null
              ? Center(
                  child: Text('Lead no encontrado',
                      style: GoogleFonts.inter(color: AppColors.textSecondary)),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildHeader(),
                      const SizedBox(height: 16),
                      _buildInfoSection('Datos de la empresa', [
                        _infoRow('Empresa', _lead!['company_name']),
                        if (_lead!['contact_name'] != null)
                          _infoRow('Contacto', _lead!['contact_name']),
                        if (_lead!['email'] != null)
                          _infoRow('Email', _lead!['email']),
                        if (_lead!['phone'] != null)
                          _infoRow('Teléfono', _lead!['phone']),
                        if (_lead!['mobile'] != null)
                          _infoRow('Celular', _lead!['mobile']),
                      ]),
                      const SizedBox(height: 16),
                      if (_lead!['street'] != null || _lead!['city'] != null)
                        _buildInfoSection('Dirección', [
                          if (_lead!['street'] != null)
                            _infoRow('Calle', _lead!['street']),
                          if (_lead!['city'] != null)
                            _infoRow('Ciudad', _lead!['city']),
                          if (_lead!['state'] != null)
                            _infoRow('Provincia', _lead!['state']),
                          if (_lead!['zip'] != null)
                            _infoRow('C.P.', _lead!['zip']),
                          if (_lead!['country'] != null)
                            _infoRow('País', _lead!['country']),
                        ]),
                      const SizedBox(height: 16),
                      if (_lead!['vat'] != null)
                        _buildInfoSection('Información fiscal', [
                          _infoRow('CUIT', _lead!['vat']),
                        ]),
                      if (_lead!['notes'] != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: _buildInfoSection('Notas', [
                            _infoRow('', _lead!['notes']),
                          ]),
                        ),
                      if (_lead!['rejection_reason'] != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: Card(
                            color: AppColors.error.withValues(alpha: 0.05),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Row(
                                children: [
                                  const Icon(Icons.error_outline, color: AppColors.error),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Motivo de rechazo',
                                            style: GoogleFonts.inter(
                                                fontWeight: FontWeight.w600,
                                                color: AppColors.error)),
                                        const SizedBox(height: 4),
                                        Text(_lead!['rejection_reason'],
                                            style: GoogleFonts.inter(color: AppColors.error)),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      if (_lead!['odoo_crm_lead_id'] != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: Card(
                            color: AppColors.primary.withValues(alpha: 0.05),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Row(
                                children: [
                                  const Icon(Icons.track_changes, color: AppColors.primary),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Lead creado en CRM de Odoo',
                                            style: GoogleFonts.inter(
                                                fontWeight: FontWeight.w600,
                                                color: AppColors.primary)),
                                        const SizedBox(height: 4),
                                        Text('ID CRM: ${_lead!['odoo_crm_lead_id']} — Pendiente de revisión por el equipo interno',
                                            style: GoogleFonts.inter(color: AppColors.primary, fontSize: 13)),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      if (_lead!['odoo_partner_id'] != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: Card(
                            color: AppColors.success.withValues(alpha: 0.05),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Row(
                                children: [
                                  const Icon(Icons.check_circle, color: AppColors.success),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Cliente creado en Odoo',
                                            style: GoogleFonts.inter(
                                                fontWeight: FontWeight.w600,
                                                color: AppColors.success)),
                                        const SizedBox(height: 4),
                                        Text('ID Odoo: ${_lead!['odoo_partner_id']}',
                                            style: GoogleFonts.inter(color: AppColors.success)),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildHeader() {
    final state = _lead!['status'] as String? ?? 'pendiente';
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Container(
              width: 56, height: 56,
              decoration: BoxDecoration(
                color: _stateColor(state).withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(Icons.business, color: _stateColor(state), size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _lead!['company_name'] ?? '',
                    style: GoogleFonts.inter(fontSize: 20, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: _stateColor(state).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _stateLabel(state),
                      style: GoogleFonts.inter(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: _stateColor(state)),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoSection(String title, List<Widget> rows) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14)),
            const SizedBox(height: 12),
            ...rows,
          ],
        ),
      ),
    );
  }

  Widget _infoRow(String label, String? value) {
    if (value == null || value.isEmpty) return const SizedBox();
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (label.isNotEmpty)
            SizedBox(
              width: 100,
              child: Text(label,
                  style: GoogleFonts.inter(
                      fontSize: 13, color: AppColors.textSecondary)),
            ),
          Expanded(
            child: Text(value ?? '',
                style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w500)),
          ),
        ],
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
