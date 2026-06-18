import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../models/client_model.dart';
import '../models/contact_model.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../services/api_service.dart';

class ClientesScreen extends StatefulWidget {
  const ClientesScreen({super.key});

  @override
  State<ClientesScreen> createState() => _ClientesScreenState();
}

class _ClientesScreenState extends State<ClientesScreen> {
  late Future<List<Client>> _clientsFuture;
  List<Client> _allClients = [];
  List<Client> _filteredClients = [];
  final _searchController = TextEditingController();
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _clientsFuture = _fetchClients();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<List<Client>> _fetchClients() async {
    final apiService = Provider.of<ApiService>(context, listen: false);
    final data = await apiService.getCustomers();
    final clients = data.map((json) => Client.fromJson(json)).toList();
    if (mounted) {
      setState(() {
        _allClients = clients;
        _filteredClients = clients;
        _loaded = true;
      });
    }
    return clients;
  }

  void _filterClients(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredClients = _allClients;
      } else {
        final q = query.toLowerCase();
        _filteredClients = _allClients.where((c) =>
          c.name.toLowerCase().contains(q) ||
          c.email.toLowerCase().contains(q) ||
          c.phone.toLowerCase().contains(q) ||
          c.cuit.toLowerCase().contains(q) ||
          c.vendedorInterno.toLowerCase().contains(q) ||
          c.address.toLowerCase().contains(q)
        ).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Clientes', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                _loaded = false;
                _clientsFuture = _fetchClients();
              });
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Client>>(
        future: _clientsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting && !_loaded) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError && !_loaded) {
            return Center(
              child: Text(
                'Error al cargar clientes',
                style: GoogleFonts.inter(color: Colors.red),
              ),
            );
          }

          final empty = _filteredClients.isEmpty && _loaded;

          if (context.isDesktop) {
            return Column(
              children: [
                _buildSearchBar(),
                Expanded(
                  child: empty
                      ? Center(
                          child: Text(
                            'No se encontraron clientes',
                            style: GoogleFonts.inter(color: AppColors.textSecondary),
                          ),
                        )
                      : SingleChildScrollView(
                          padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
                          child: DataTable(
                            headingRowColor: WidgetStateProperty.all(AppColors.background),
                            columnSpacing: 24,
                            columns: const [
                              DataColumn(label: Text('Nombre', style: TextStyle(fontWeight: FontWeight.w600))),
                              DataColumn(label: Text('CUIT', style: TextStyle(fontWeight: FontWeight.w600))),
                              DataColumn(label: Text('Email', style: TextStyle(fontWeight: FontWeight.w600))),
                              DataColumn(label: Text('Teléfono', style: TextStyle(fontWeight: FontWeight.w600))),
                              DataColumn(label: Text('Dirección', style: TextStyle(fontWeight: FontWeight.w600))),
                              DataColumn(label: Text('', style: TextStyle(fontWeight: FontWeight.w600))),
                            ],
                            rows: _filteredClients.map((c) => DataRow(cells: [
                              DataCell(Text(c.name, style: const TextStyle(fontWeight: FontWeight.w500))),
                              DataCell(Text(c.cuit)),
                              DataCell(Text(c.email)),
                              DataCell(Text(c.phone)),
                              DataCell(Text(c.address, overflow: TextOverflow.ellipsis)),
                              DataCell(
                                Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    FilledButton.tonal(
                                      onPressed: () => context.push('/customers/budget/create', extra: c),
                                      style: FilledButton.styleFrom(minimumSize: const Size(0, 32)),
                                      child: const Text('Presupuesto', style: TextStyle(fontSize: 12)),
                                    ),
                                    const SizedBox(width: 8),
                                    OutlinedButton(
                                      onPressed: () => _showContactDialog(c),
                                      style: OutlinedButton.styleFrom(minimumSize: const Size(0, 32)),
                                      child: const Text('Ver contacto', style: TextStyle(fontSize: 12)),
                                    ),
                                  ],
                                ),
                              ),
                            ])).toList(),
                          ),
                        ),
                ),
              ],
            );
          }

          return Column(
            children: [
              _buildSearchBar(),
              Expanded(
                child: empty
                    ? Center(
                        child: Text(
                          'No se encontraron clientes',
                          style: GoogleFonts.inter(color: AppColors.textSecondary),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _filteredClients.length,
                        itemBuilder: (context, index) => Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: _ClientCard(
                            client: _filteredClients[index],
                            onViewContact: _showContactDialog,
                          ),
                        ),
                      ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
      child: TextField(
        controller: _searchController,
        onChanged: _filterClients,
        decoration: InputDecoration(
          hintText: 'Buscar clientes...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                    _filterClients('');
                  },
                )
              : null,
          isDense: true,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
      ),
    );
  }

  void _showContactDialog(Client client) {
    showDialog(
      context: context,
      builder: (ctx) => _ContactDialog(client: client),
    );
  }

}

class _ClientCard extends StatelessWidget {
  final Client client;
  final void Function(Client) onViewContact;
  const _ClientCard({required this.client, required this.onViewContact});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.divider),
        boxShadow: const [
          BoxShadow(
            color: AppColors.cardShadow,
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor: AppColors.primary.withOpacity(0.12),
                  child: Text(
                    client.initials,
                    style: GoogleFonts.inter(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: AppColors.primary,
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        client.name,
                        style: GoogleFonts.inter(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      if (client.companyName.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          client.companyName,
                          style: GoogleFonts.inter(
                            fontSize: 13,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
            if (client.email.isNotEmpty) ...[
              const SizedBox(height: 16),
              Row(
                children: [
                  const Icon(Icons.email_outlined, size: 16, color: AppColors.textSecondary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      client.email,
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            ],
            if (client.phone.isNotEmpty) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.phone_outlined, size: 16, color: AppColors.textSecondary),
                  const SizedBox(width: 8),
                  Text(
                    client.phone,
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ],
            if (client.address.isNotEmpty) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.location_on_outlined, size: 16, color: AppColors.textSecondary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      client.address,
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            ],
            if (client.cuit.isNotEmpty) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.badge_outlined, size: 16, color: AppColors.textSecondary),
                  const SizedBox(width: 8),
                  Text(
                    'CUIT: ${client.cuit}',
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ],
            if (client.vendedorInterno.isNotEmpty) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.person_outline, size: 16, color: AppColors.textSecondary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Vend. int.: ${client.vendedorInterno}',
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton(
                  onPressed: () => onViewContact(client),
                  child: const Text('Ver contacto'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () {
                    context.push('/customers/budget/create', extra: client);
                  },
                  child: const Text('Crear presupuesto'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ContactDialog extends StatefulWidget {
  final Client client;
  const _ContactDialog({required this.client});

  @override
  State<_ContactDialog> createState() => _ContactDialogState();
}

class _ContactDialogState extends State<_ContactDialog> {
  late Future<List<Contact>> _contactsFuture;

  @override
  void initState() {
    super.initState();
    _contactsFuture = _fetchContacts();
  }

  Future<List<Contact>> _fetchContacts() async {
    final api = context.read<ApiService>();
    final data = await api.getContacts(widget.client.id);
    return data.map((j) => Contact.fromJson(j)).toList();
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.client;
    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520),
        child: Material(
          borderRadius: BorderRadius.circular(18),
          color: AppColors.surface,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    CircleAvatar(
                      radius: 20,
                      backgroundColor: AppColors.primary.withOpacity(0.12),
                      child: Text(
                        c.initials,
                        style: GoogleFonts.inter(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(c.name, style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                          if (c.companyName.isNotEmpty)
                            Text(c.companyName, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary)),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const Divider(height: 24),
                _infoRow(Icons.badge_outlined, 'CUIT', c.cuit),
                _infoRow(Icons.email_outlined, 'Email', c.email),
                _infoRow(Icons.phone_outlined, 'Teléfono', c.phone),
                _infoRow(Icons.phone_android_outlined, 'Celular', c.mobile),
                _infoRow(Icons.location_on_outlined, 'Dirección', c.address),
                _infoRow(Icons.person_outline, 'Vendedor interno', c.vendedorInterno),
                _infoRow(Icons.people_outline, 'Empresa', c.companyName),
                _infoRow(Icons.language_outlined, 'Sitio web', c.website),
                if (c.salespersonEmail != null)
                  _infoRow(Icons.supervisor_account_outlined, 'Vendedor externo', c.salespersonEmail!),
                const SizedBox(height: 16),
                Text('Contactos', style: GoogleFonts.inter(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                const SizedBox(height: 8),
                FutureBuilder<List<Contact>>(
                  future: _contactsFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()));
                    }
                    if (snapshot.hasError) {
                      return Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text('Error al cargar contactos', style: GoogleFonts.inter(color: Colors.red, fontSize: 13)),
                      );
                    }
                    final contacts = snapshot.data ?? [];
                    if (contacts.isEmpty) {
                      return Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text('Sin contactos adicionales', style: GoogleFonts.inter(color: AppColors.textSecondary, fontSize: 13)),
                      );
                    }
                    return ConstrainedBox(
                      constraints: const BoxConstraints(maxHeight: 200),
                      child: ListView.separated(
                        shrinkWrap: true,
                        itemCount: contacts.length,
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (_, i) {
                          final contact = contacts[i];
                          return ListTile(
                            dense: true,
                            leading: CircleAvatar(
                              radius: 16,
                              backgroundColor: AppColors.primary.withOpacity(0.08),
                              child: Text(
                                contact.name.isNotEmpty ? contact.name[0].toUpperCase() : '?',
                                style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.primary),
                              ),
                            ),
                            title: Text(contact.name, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500)),
                            subtitle: contact.email.isNotEmpty || contact.phone.isNotEmpty
                                ? Text([contact.email, contact.phone].where((e) => e.isNotEmpty).join(' · '), style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary))
                                : null,
                          );
                        },
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _infoRow(IconData icon, String label, String value) {
    if (value.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Icon(icon, size: 16, color: AppColors.textSecondary),
          const SizedBox(width: 8),
          Text('$label: ', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textSecondary)),
          Expanded(
            child: Text(value, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textPrimary)),
          ),
        ],
      ),
    );
  }
}
