import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';

class ResponsiveShell extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const ResponsiveShell({super.key, required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    return context.isDesktop
        ? _DesktopShell(navigationShell: navigationShell)
        : _MobileShell(navigationShell: navigationShell);
  }
}

class _DesktopShell extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const _DesktopShell({required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        NavigationRail(
          selectedIndex: navigationShell.currentIndex,
          onDestinationSelected: (i) => navigationShell.goBranch(i),
          labelType: NavigationRailLabelType.all,
          minWidth: 80,
          groupAlignment: -1,
          backgroundColor: AppColors.surface,
          leading: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: CircleAvatar(
              radius: 18,
              backgroundColor: AppColors.accent,
              child: Text('B', style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white)),
            ),
          ),
          destinations: const [
            NavigationRailDestination(
              icon: Icon(Icons.dashboard_rounded),
              selectedIcon: Icon(Icons.dashboard_rounded),
              label: Text('Dashboard'),
            ),
            NavigationRailDestination(
              icon: Icon(Icons.people_alt_rounded),
              selectedIcon: Icon(Icons.people_alt_rounded),
              label: Text('Clientes'),
            ),
            NavigationRailDestination(
              icon: Icon(Icons.solar_power_rounded),
              selectedIcon: Icon(Icons.solar_power_rounded),
              label: Text('Productos'),
            ),
            NavigationRailDestination(
              icon: Icon(Icons.receipt_long_rounded),
              selectedIcon: Icon(Icons.receipt_long_rounded),
              label: Text('Presupuestos'),
            ),
          ],
        ),
        const VerticalDivider(width: 1, thickness: 1),
        Expanded(child: navigationShell),
      ],
    );
  }
}

class _MobileShell extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const _MobileShell({required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: (i) => navigationShell.goBranch(i),
        backgroundColor: AppColors.surface,
        indicatorColor: AppColors.primary.withOpacity(0.12),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_rounded), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.people_alt_rounded), label: 'Clientes'),
          NavigationDestination(icon: Icon(Icons.solar_power_rounded), label: 'Productos'),
          NavigationDestination(icon: Icon(Icons.receipt_long_rounded), label: 'Presupuestos'),
        ],
      ),
    );
  }
}
