import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:dio/dio.dart';
import '../services/auth_provider.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../widgets/stat_card.dart';
import '../services/api_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _clientCount = 0;
  int _orderCount = 0;
  int _productCount = 0;
  bool _loadingStats = true;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      final api = context.read<ApiService>();
      final clients = await api.getCustomers();
      final orders = await api.getOrders();
      final products = await api.getProducts();
      if (mounted) {
        setState(() {
          _clientCount = clients.length;
          _orderCount = orders.length;
          _productCount = products.length;
          _loadingStats = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loadingStats = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final user = auth.user;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 140,
            floating: false,
            pinned: true,
            backgroundColor: AppColors.primary,
            actions: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined, color: Colors.white),
                onPressed: () {},
              ),
              _UserAvatar(user: user, onLogout: () => _logout(context, auth)),
              const SizedBox(width: 8),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [AppColors.primary, AppColors.primaryLight],
                  ),
                ),
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                child: Align(
                  alignment: Alignment.bottomLeft,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _greeting(),
                        style: GoogleFonts.inter(fontSize: 13, color: Colors.white.withOpacity(0.7)),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        user?.name ?? 'Usuario',
                        style: GoogleFonts.inter(fontSize: 22, fontWeight: FontWeight.w700, color: Colors.white),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 0),
              child: Text(
                'Resumen',
                style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
              child: _loadingStats
                  ? const Center(child: CircularProgressIndicator())
                  : _StatsSection(
                      clientCount: _clientCount,
                      orderCount: _orderCount,
                      productCount: _productCount,
                    ),
            ),
          ),
          if (!context.isDesktop) ...[
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                child: Text(
                  'Acceso rápido',
                  style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
              sliver: SliverGrid(
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: Responsive.gridColumns(context),
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                  childAspectRatio: 1.15,
                ),
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final item = _quickItems[index];
                    return _QuickCard(
                      icon: item.icon,
                      label: item.label,
                      color: item.color,
                      onTap: () => _navigateTo(context, item.route),
                    );
                  },
                  childCount: _quickItems.length,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _greeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Buenos días,';
    if (hour < 18) return 'Buenas tardes,';
    return 'Buenas noches,';
  }

  void _navigateTo(BuildContext context, String route) {
    context.go(route);
  }

  Future<void> _logout(BuildContext context, AuthProvider auth) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Cerrar sesión', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
        content: Text('¿Estás seguro que querés salir?', style: GoogleFonts.inter()),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(minimumSize: const Size(80, 40), backgroundColor: AppColors.error),
            child: const Text('Salir'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await auth.logout();
      if (context.mounted) context.go('/login');
    }
  }
}

class _UserAvatar extends StatelessWidget {
  final dynamic user;
  final VoidCallback onLogout;
  const _UserAvatar({required this.user, required this.onLogout});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.isDesktop
          ? showDialog(
              context: context,
              builder: (_) => _ProfileDialog(user: user, onLogout: onLogout),
            )
          : showModalBottomSheet(
              context: context,
              shape: const RoundedRectangleBorder(
                borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
              ),
              builder: (_) => _ProfileSheet(user: user, onLogout: onLogout),
            ),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: AppColors.accent,
          shape: BoxShape.circle,
          border: Border.all(color: Colors.white.withOpacity(0.3), width: 2),
        ),
        child: Center(
          child: Text(
            user?.initials ?? '?',
            style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white),
          ),
        ),
      ),
    );
  }
}

class _ProfileDialog extends StatefulWidget {
  final dynamic user;
  final VoidCallback onLogout;
  const _ProfileDialog({required this.user, required this.onLogout});

  @override
  State<_ProfileDialog> createState() => _ProfileDialogState();
}

class _ProfileDialogState extends State<_ProfileDialog> {
  bool _syncingCustomers = false;
  bool _syncingProducts = false;

  Future<void> _syncCustomers() async {
    setState(() => _syncingCustomers = true);
    try {
      await context.read<ApiService>().syncCustomers();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Clientes sincronizados correctamente')),
      );
    } catch (e) {
      if (!mounted) return;
      final msg = e is DioException ? _extractError(e) : 'Error al sincronizar clientes';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: AppColors.error),
      );
    } finally {
      if (mounted) setState(() => _syncingCustomers = false);
    }
  }

  Future<void> _syncProducts() async {
    setState(() => _syncingProducts = true);
    try {
      await context.read<ApiService>().syncProducts();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Productos sincronizados correctamente')),
      );
    } catch (e) {
      if (!mounted) return;
      final msg = e is DioException ? _extractError(e) : 'Error al sincronizar productos';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: AppColors.error),
      );
    } finally {
      if (mounted) setState(() => _syncingProducts = false);
    }
  }

  String _extractError(DioException e) {
    try {
      return e.response?.data?['detail'] ?? 'Error de conexión';
    } catch (_) {
      return 'Error de conexión';
    }
  }

  @override
  Widget build(BuildContext context) {
    final isAdmin = widget.user?.role == 'admin';
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircleAvatar(
              radius: 36,
              backgroundColor: AppColors.primary,
              child: Text(widget.user?.initials ?? '?', style: GoogleFonts.inter(fontSize: 22, fontWeight: FontWeight.w700, color: Colors.white)),
            ),
            const SizedBox(height: 12),
            Text(widget.user?.name ?? '', style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w600)),
            Text(widget.user?.email ?? '', style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary)),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
              child: Text(widget.user?.role ?? '', style: GoogleFonts.inter(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.w500)),
            ),
            if (isAdmin) ...[
              const SizedBox(height: 20),
              const Divider(),
              Text('Administración', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _SyncButton(
                      label: 'Sincronizar clientes',
                      icon: Icons.sync_alt,
                      loading: _syncingCustomers,
                      onPressed: _syncCustomers,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _SyncButton(
                      label: 'Sincronizar productos',
                      icon: Icons.sync,
                      loading: _syncingProducts,
                      onPressed: _syncProducts,
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 24),
            OutlinedButton.icon(
              onPressed: () { Navigator.pop(context); widget.onLogout(); },
              icon: const Icon(Icons.logout, color: AppColors.error),
              label: Text('Cerrar sesión', style: GoogleFonts.inter(color: AppColors.error)),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
                side: BorderSide(color: AppColors.error.withOpacity(0.3)),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProfileSheet extends StatefulWidget {
  final dynamic user;
  final VoidCallback onLogout;
  const _ProfileSheet({required this.user, required this.onLogout});

  @override
  State<_ProfileSheet> createState() => _ProfileSheetState();
}

class _ProfileSheetState extends State<_ProfileSheet> {
  bool _syncingCustomers = false;
  bool _syncingProducts = false;

  Future<void> _syncCustomers() async {
    setState(() => _syncingCustomers = true);
    try {
      await context.read<ApiService>().syncCustomers();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Clientes sincronizados correctamente')),
      );
    } catch (e) {
      if (!mounted) return;
      final msg = e is DioException ? _extractError(e) : 'Error al sincronizar clientes';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: AppColors.error),
      );
    } finally {
      if (mounted) setState(() => _syncingCustomers = false);
    }
  }

  Future<void> _syncProducts() async {
    setState(() => _syncingProducts = true);
    try {
      await context.read<ApiService>().syncProducts();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Productos sincronizados correctamente')),
      );
    } catch (e) {
      if (!mounted) return;
      final msg = e is DioException ? _extractError(e) : 'Error al sincronizar productos';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: AppColors.error),
      );
    } finally {
      if (mounted) setState(() => _syncingProducts = false);
    }
  }

  String _extractError(DioException e) {
    try {
      return e.response?.data?['detail'] ?? 'Error de conexión';
    } catch (_) {
      return 'Error de conexión';
    }
  }

  @override
  Widget build(BuildContext context) {
    final isAdmin = widget.user?.role == 'admin';
    return Padding(
      padding: const EdgeInsets.all(24),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(width: 40, height: 4, decoration: BoxDecoration(color: AppColors.divider, borderRadius: BorderRadius.circular(2))),
            const SizedBox(height: 20),
            CircleAvatar(
              radius: 36,
              backgroundColor: AppColors.primary,
              child: Text(widget.user?.initials ?? '?', style: GoogleFonts.inter(fontSize: 22, fontWeight: FontWeight.w700, color: Colors.white)),
            ),
            const SizedBox(height: 12),
            Text(widget.user?.name ?? '', style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w600)),
            Text(widget.user?.email ?? '', style: GoogleFonts.inter(fontSize: 14, color: AppColors.textSecondary)),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
              child: Text(widget.user?.role ?? '', style: GoogleFonts.inter(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.w500)),
            ),
            if (isAdmin) ...[
              const SizedBox(height: 20),
              const Divider(),
              Text('Administración', style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _SyncButton(
                      label: 'Sincronizar clientes',
                      icon: Icons.sync_alt,
                      loading: _syncingCustomers,
                      onPressed: _syncCustomers,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _SyncButton(
                      label: 'Sincronizar productos',
                      icon: Icons.sync,
                      loading: _syncingProducts,
                      onPressed: _syncProducts,
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 24),
            OutlinedButton.icon(
              onPressed: () { Navigator.pop(context); widget.onLogout(); },
              icon: const Icon(Icons.logout, color: AppColors.error),
              label: Text('Cerrar sesión', style: GoogleFonts.inter(color: AppColors.error)),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
                side: BorderSide(color: AppColors.error.withOpacity(0.3)),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SyncButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool loading;
  final VoidCallback onPressed;

  const _SyncButton({
    required this.label,
    required this.icon,
    required this.loading,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 80,
      child: OutlinedButton(
        onPressed: loading ? null : onPressed,
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          side: BorderSide(color: AppColors.primary.withOpacity(0.3)),
        ),
        child: loading
            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(icon, color: AppColors.primary, size: 22),
                  const SizedBox(height: 6),
                  Text(label, style: GoogleFonts.inter(fontSize: 11, color: AppColors.primary, fontWeight: FontWeight.w500), textAlign: TextAlign.center),
                ],
              ),
      ),
    );
  }
}

class _QuickItem {
  final IconData icon;
  final String label;
  final Color color;
  final String route;
  const _QuickItem({required this.icon, required this.label, required this.color, required this.route});
}

final _quickItems = [
  _QuickItem(icon: Icons.people_alt_rounded, label: 'Clientes', color: const Color(0xFF2D9CDB), route: '/customers'),
  _QuickItem(icon: Icons.receipt_long_rounded, label: 'Cotizaciones', color: const Color(0xFF5E60CE), route: '/quotations'),
  _QuickItem(icon: Icons.solar_power_rounded, label: 'Productos', color: const Color(0xFFF4A900), route: '/products'),
];

class _QuickCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickCard({required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.surface,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onTap,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: AppColors.divider),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(14)),
                child: Icon(icon, color: color, size: 24),
              ),
              const SizedBox(height: 10),
              Text(label, style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14, color: AppColors.textPrimary)),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatsSection extends StatelessWidget {
  final int clientCount;
  final int orderCount;
  final int productCount;

  const _StatsSection({required this.clientCount, required this.orderCount, required this.productCount});

  @override
  Widget build(BuildContext context) {
    final cards = <StatCard>[
      StatCard(label: 'Clientes', value: clientCount.toString(), delta: '', positive: true, icon: Icons.people_alt_rounded, iconColor: const Color(0xFF2D9CDB)),
      StatCard(label: 'Presupuestos', value: orderCount.toString(), delta: '', positive: true, icon: Icons.receipt_long_rounded, iconColor: const Color(0xFF5E60CE)),
      StatCard(label: 'Productos', value: productCount.toString(), delta: '', positive: true, icon: Icons.solar_power_rounded, iconColor: AppColors.accent),
    ];

    if (context.isPhone) {
      return SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        clipBehavior: Clip.none,
        child: Row(
          children: cards
              .map((card) => Padding(
                    padding: const EdgeInsets.only(right: 12),
                    child: SizedBox(width: 140, child: card),
                  ))
              .toList(),
        ),
      );
    }

    if (context.isTablet) {
      return Wrap(
        spacing: 12,
        runSpacing: 12,
        children: cards
            .map((card) => SizedBox(
                  width: (MediaQuery.of(context).size.width - 44) / 2,
                  child: card,
                ))
            .toList(),
      );
    }

    return Row(
      children: cards
          .map((card) => Expanded(child: Padding(
                padding: const EdgeInsets.only(right: 12),
                child: card,
              )))
          .toList(),
    );
  }
}
