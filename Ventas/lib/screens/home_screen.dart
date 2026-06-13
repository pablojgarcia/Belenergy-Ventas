import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/auth_provider.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../widgets/menu_card.dart';
import '../widgets/stat_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  static final List<_MenuItem> _menuItems = [
    const _MenuItem(
      icon: Icons.people_alt_rounded,
      label: 'Clientes',
      subtitle: 'Cartera de clientes',
      color: Color(0xFF2D9CDB),
      route: '/customers',
    ),
    const _MenuItem(
      icon: Icons.bolt_rounded,
      label: 'Presupuestos',
      subtitle: 'Crear y gestionar',
      color: Color(0xFF5E60CE),
      route: '/orders',
    ),
    const _MenuItem(
      icon: Icons.solar_power_rounded,
      label: 'Productos',
      subtitle: 'Catálogo FV',
      color: Color(0xFFF4A900),
      route: '/products',
    ),
    const _MenuItem(
      icon: Icons.receipt_long_rounded,
      label: 'Pedidos',
      subtitle: 'Órdenes activas',
      color: Color(0xFF27AE60),
      route: '/orders',
    ),
    /* const _MenuItem(
      icon: Icons.bar_chart_rounded,
      label: 'Reportes',
      subtitle: 'Ventas y métricas',
      color: Color(0xFFEB5757),
      route: '/reportes',
    ),
    const _MenuItem(
      icon: Icons.inventory_2_rounded,
      label: 'Stock',
      subtitle: 'Inventario Odoo',
      color: Color(0xFF6FCF97),
      route: '/stock',
    ),
    const _MenuItem(
      icon: Icons.build_circle_rounded,
      label: 'Instalaciones',
      subtitle: 'Proyectos en curso',
      color: Color(0xFFF2994A),
      route: '/instalaciones',
    ),
    const _MenuItem(
      icon: Icons.support_agent_rounded,
      label: 'Soporte',
      subtitle: 'Post-venta',
      color: Color(0xFF9B51E0),
      route: '/soporte',
    ),*/
  ];

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final user = auth.user;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: CustomScrollView(
        slivers: [
          // ── App Bar ──────────────────────────────────────────────────────
          SliverAppBar(
            expandedHeight: 140,
            floating: false,
            pinned: true,
            backgroundColor: AppColors.primary,
            actions: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined,
                    color: Colors.white),
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
                        style: GoogleFonts.inter(
                          fontSize: 13,
                          color: Colors.white.withOpacity(0.7),
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        user?.name ?? 'Usuario',
                        style: GoogleFonts.inter(
                          fontSize: 22,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // ── Stats ─────────────────────────────────────────────────────────
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Resumen del mes',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _StatsSection(),
                ],
              ),
            ),
          ),

          // ── Menu grid ────────────────────────────────────────────────────
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
              child: Text(
                'Módulos',
                style: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
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
                  final item = _menuItems[index];
                  return MenuCard(
                    icon: item.icon,
                    label: item.label,
                    subtitle: item.subtitle,
                    color: item.color,
                    onTap: () => _navigateTo(context, item.route),
                  );
                },
                childCount: _menuItems.length,
              ),
            ),
          ),
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
        title: Text('Cerrar sesión',
            style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
        content: Text('¿Estás seguro que querés salir?',
            style: GoogleFonts.inter()),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              minimumSize: const Size(80, 40),
              backgroundColor: AppColors.error,
            ),
            child: const Text('Salir'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await auth.logout();
      if (context.mounted) {
        context.go('/login');
      }
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
      onTap: () => showModalBottomSheet(
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
            style: GoogleFonts.inter(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
        ),
      ),
    );
  }
}

class _ProfileSheet extends StatelessWidget {
  final dynamic user;
  final VoidCallback onLogout;

  const _ProfileSheet({required this.user, required this.onLogout});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: AppColors.divider,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 20),
          CircleAvatar(
            radius: 36,
            backgroundColor: AppColors.primary,
            child: Text(
              user?.initials ?? '?',
              style: GoogleFonts.inter(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  color: Colors.white),
            ),
          ),
          const SizedBox(height: 12),
          Text(user?.name ?? '',
              style: GoogleFonts.inter(
                  fontSize: 18, fontWeight: FontWeight.w600)),
          Text(user?.email ?? '',
              style: GoogleFonts.inter(
                  fontSize: 14, color: AppColors.textSecondary)),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              user?.role ?? '',
              style: GoogleFonts.inter(
                  fontSize: 12,
                  color: AppColors.primary,
                  fontWeight: FontWeight.w500),
            ),
          ),
          const SizedBox(height: 24),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.pop(context);
              onLogout();
            },
            icon: const Icon(Icons.logout, color: AppColors.error),
            label: Text('Cerrar sesión',
                style: GoogleFonts.inter(color: AppColors.error)),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(double.infinity, 48),
              side: BorderSide(color: AppColors.error.withOpacity(0.3)),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}

class _MenuItem {
  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;
  final String route;

  const _MenuItem({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.color,
    required this.route,
  });
}

const _statCards = [
  StatCard(
    label: 'Presupuestos',
    value: '12',
    delta: '+3',
    positive: true,
    icon: Icons.bolt_rounded,
    iconColor: Color(0xFF5E60CE),
  ),
  StatCard(
    label: 'kWp vendidos',
    value: '48.5',
    delta: '+12%',
    positive: true,
    icon: Icons.solar_power_rounded,
    iconColor: AppColors.accent,
  ),
  StatCard(
    label: 'Pedidos pend.',
    value: '5',
    delta: '-2',
    positive: false,
    icon: Icons.receipt_long_rounded,
    iconColor: Color(0xFFEB5757),
  ),
];

class _StatsSection extends StatelessWidget {
  const _StatsSection();

  @override
  Widget build(BuildContext context) {
    if (context.isPhone) {
      return SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        clipBehavior: Clip.none,
        child: Row(
          children: _statCards
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
        children: _statCards
            .map((card) => SizedBox(
                  width: (MediaQuery.of(context).size.width - 44) / 2,
                  child: card,
                ))
            .toList(),
      );
    }

    return Row(
      children: _statCards
          .map((card) => Expanded(child: Padding(
                padding: const EdgeInsets.only(right: 12),
                child: card,
              )))
          .toList(),
    );
  }
}
