import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';

class ResponsiveShell extends StatelessWidget {
  final Widget child;

  const ResponsiveShell({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return context.isDesktop
        ? _DesktopShell(child: child)
        : _MobileShell(child: child);
  }
}

int _currentTab(String location) {
  if (location == '/') return 0;
  if (location == '/customers') return 1;
  if (location == '/products') return 2;
  if (location.startsWith('/quotations')) return 3;
  return 0;
}

class _DesktopShell extends StatelessWidget {
  final Widget child;

  const _DesktopShell({required this.child});

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    final selectedIndex = _currentTab(location);
    return Row(
      children: [
        NavigationRail(
          selectedIndex: selectedIndex,
          onDestinationSelected: (i) {
            switch (i) {
              case 0: context.go('/');
              case 1: context.go('/customers');
              case 2: context.go('/products');
              case 3: context.go('/quotations');
            }
          },
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
              label: Text('Cotizaciones'),
            ),
          ],
        ),
        const VerticalDivider(width: 1, thickness: 1),
        Expanded(child: child),
      ],
    );
  }
}

class _MobileShell extends StatelessWidget {
  final Widget child;

  const _MobileShell({required this.child});

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    final selectedIndex = _currentTab(location);
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: (i) {
          switch (i) {
            case 0: context.go('/');
            case 1: context.go('/customers');
            case 2: context.go('/products');
            case 3: context.go('/quotations');
          }
        },
        backgroundColor: AppColors.surface,
        indicatorColor: AppColors.primary.withOpacity(0.12),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_rounded), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.people_alt_rounded), label: 'Clientes'),
          NavigationDestination(icon: Icon(Icons.solar_power_rounded), label: 'Productos'),
          NavigationDestination(icon: Icon(Icons.receipt_long_rounded), label: 'Cotizaciones'),
        ],
      ),
    );
  }
}
