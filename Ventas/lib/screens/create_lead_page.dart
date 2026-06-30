import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

class CreateLeadPage extends StatefulWidget {
  final String? leadId;

  const CreateLeadPage({super.key, this.leadId});

  @override
  State<CreateLeadPage> createState() => _CreateLeadPageState();
}

class _CreateLeadPageState extends State<CreateLeadPage> {
  final _formKey = GlobalKey<FormState>();
  final _companyNameController = TextEditingController();
  final _contactNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _mobileController = TextEditingController();
  final _streetController = TextEditingController();
  final _cityController = TextEditingController();
  final _stateController = TextEditingController();
  final _zipController = TextEditingController();
  final _countryController = TextEditingController();
  final _vatController = TextEditingController();
  final _notesController = TextEditingController();
  bool _loading = false;
  bool _isEditing = false;
  int _version = 1;

  @override
  void initState() {
    super.initState();
    if (widget.leadId != null) {
      _isEditing = true;
      _loadLead();
    }
  }

  Future<void> _loadLead() async {
    setState(() => _loading = true);
    final api = context.read<ApiService>();
    try {
      final lead = await api.getLead(widget.leadId!);
      if (lead == null || !mounted) return;
      _companyNameController.text = lead['company_name'] ?? '';
      _contactNameController.text = lead['contact_name'] ?? '';
      _emailController.text = lead['email'] ?? '';
      _phoneController.text = lead['phone'] ?? '';
      _mobileController.text = lead['mobile'] ?? '';
      _streetController.text = lead['street'] ?? '';
      _cityController.text = lead['city'] ?? '';
      _stateController.text = lead['state'] ?? '';
      _zipController.text = lead['zip'] ?? '';
      _countryController.text = lead['country'] ?? '';
      _vatController.text = lead['vat'] ?? '';
      _notesController.text = lead['notes'] ?? '';
      _version = lead['version'] ?? 1;
      if (mounted) setState(() => _loading = false);
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error al cargar el lead')),
        );
      }
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _loading = true);
    final api = context.read<ApiService>();
    final Map<String, dynamic> data = {
      'company_name': _companyNameController.text.trim(),
      'contact_name': _contactNameController.text.trim().isEmpty
          ? null : _contactNameController.text.trim(),
      'email': _emailController.text.trim().isEmpty
          ? null : _emailController.text.trim(),
      'phone': _phoneController.text.trim().isEmpty
          ? null : _phoneController.text.trim(),
      'mobile': _mobileController.text.trim().isEmpty
          ? null : _mobileController.text.trim(),
      'street': _streetController.text.trim().isEmpty
          ? null : _streetController.text.trim(),
      'city': _cityController.text.trim().isEmpty
          ? null : _cityController.text.trim(),
      'state': _stateController.text.trim().isEmpty
          ? null : _stateController.text.trim(),
      'zip': _zipController.text.trim().isEmpty
          ? null : _zipController.text.trim(),
      'country': _countryController.text.trim().isEmpty
          ? null : _countryController.text.trim(),
      'vat': _vatController.text.trim().isEmpty
          ? null : _vatController.text.trim(),
      'notes': _notesController.text.trim().isEmpty
          ? null : _notesController.text.trim(),
    };

    try {
      if (_isEditing) {
        data['version'] = _version;
        await api.updateLead(widget.leadId!, data);
      } else {
        await api.createLead(data);
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(_isEditing ? 'Lead actualizado' : 'Lead creado'),
            backgroundColor: AppColors.success,
          ),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        final msg = e is DioException
            ? (e.response?.data?['detail'] ?? 'Error de conexión')
            : 'Error al guardar';
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
        title: Text(
          _isEditing ? 'Editar lead' : 'Nuevo lead',
          style: GoogleFonts.inter(),
        ),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
        actions: [
          TextButton(
            onPressed: _loading ? null : _save,
            child: _loading
                ? const SizedBox(
                    width: 18, height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(
                    _isEditing ? 'Guardar' : 'Crear',
                    style: GoogleFonts.inter(fontWeight: FontWeight.w600),
                  ),
          ),
        ],
      ),
      body: _loading && _isEditing
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _buildSectionCard(
                      icon: Icons.business,
                      title: 'Empresa',
                      children: [
                        _buildField(
                          controller: _companyNameController,
                          label: 'Nombre de la empresa',
                          icon: Icons.business,
                          required: true,
                          validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
                        ),
                        const SizedBox(height: 14),
                        _buildField(
                          controller: _contactNameController,
                          label: 'Nombre del contacto',
                          icon: Icons.person,
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _buildSectionCard(
                      icon: Icons.contact_mail,
                      title: 'Contacto',
                      children: [
                        _buildField(
                          controller: _emailController,
                          label: 'Correo electrónico',
                          icon: Icons.email_outlined,
                          keyboardType: TextInputType.emailAddress,
                        ),
                        const SizedBox(height: 14),
                        Row(
                          children: [
                            Expanded(
                              child: _buildField(
                                controller: _phoneController,
                                label: 'Teléfono',
                                icon: Icons.phone_outlined,
                                keyboardType: TextInputType.phone,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildField(
                                controller: _mobileController,
                                label: 'Celular',
                                icon: Icons.smartphone_outlined,
                                keyboardType: TextInputType.phone,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _buildSectionCard(
                      icon: Icons.location_on_outlined,
                      title: 'Dirección',
                      children: [
                        _buildField(
                          controller: _streetController,
                          label: 'Calle',
                          icon: Icons.streetview,
                        ),
                        const SizedBox(height: 14),
                        Row(
                          children: [
                            Expanded(
                              child: _buildField(
                                controller: _cityController,
                                label: 'Ciudad',
                                icon: Icons.location_city,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildField(
                                controller: _stateController,
                                label: 'Provincia',
                                icon: Icons.map_outlined,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 14),
                        Row(
                          children: [
                            Expanded(
                              child: _buildField(
                                controller: _zipController,
                                label: 'Código postal',
                                icon: Icons.markunread_mailbox_outlined,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildField(
                                controller: _countryController,
                                label: 'País',
                                icon: Icons.public,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _buildSectionCard(
                      icon: Icons.receipt_outlined,
                      title: 'Información fiscal',
                      children: [
                        _buildField(
                          controller: _vatController,
                          label: 'CUIT',
                          icon: Icons.numbers,
                          required: true,
                          validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _buildSectionCard(
                      icon: Icons.notes_outlined,
                      title: 'Notas',
                      children: [
                        _buildField(
                          controller: _notesController,
                          label: 'Notas internas',
                          icon: Icons.edit_note,
                          maxLines: 3,
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton.icon(
                      onPressed: _loading ? null : _save,
                      icon: _loading
                          ? const SizedBox(
                              width: 18, height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : const Icon(Icons.save),
                      label: Text(_isEditing ? 'Guardar cambios' : 'Crear lead'),
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildSectionCard({
    required IconData icon,
    required String title,
    required List<Widget> children,
  }) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 32, height: 32,
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, size: 18, color: AppColors.primary),
                ),
                const SizedBox(width: 10),
                Text(
                  title,
                  style: GoogleFonts.inter(
                    fontWeight: FontWeight.w600,
                    fontSize: 15,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool required = false,
    int maxLines = 1,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      maxLines: maxLines,
      keyboardType: keyboardType,
      validator: validator,
      decoration: InputDecoration(
        labelText: required ? '$label *' : label,
        prefixIcon: Icon(icon, size: 20),
        isDense: true,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      ),
    );
  }

  @override
  void dispose() {
    _companyNameController.dispose();
    _contactNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _mobileController.dispose();
    _streetController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _zipController.dispose();
    _countryController.dispose();
    _vatController.dispose();
    _notesController.dispose();
    super.dispose();
  }
}
