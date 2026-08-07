import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../services/auth_provider.dart';

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

int _currentTab(String location, bool isAdmin) {
  if (location == '/') return 0;
  if (location == '/customers') return 1;
  if (location == '/products') return 2;
  if (location.startsWith('/quotations')) return 3;
  if (isAdmin && location == '/admin/discount-rules') return 4;
  return 0;
}

void _navigateTo(BuildContext context, int i) {
  switch (i) {
    case 0: context.go('/');
    case 1: context.go('/customers');
    case 2: context.go('/products');
    case 3: context.go('/quotations');
    case 4: context.go('/admin/discount-rules');
  }
}

class _DesktopShell extends StatelessWidget {
  final Widget child;

  const _DesktopShell({required this.child});

  @override
  Widget build(BuildContext context) {
    final isAdmin = context.watch<AuthProvider>().isAdmin;
    final location = GoRouterState.of(context).matchedLocation;
    final selectedIndex = _currentTab(location, isAdmin);
    return Row(
      children: [
        NavigationRail(
          selectedIndex: selectedIndex,
          onDestinationSelected: (i) => _navigateTo(context, i),
          labelType: NavigationRailLabelType.all,
          minWidth: 80,
          groupAlignment: -1,
          backgroundColor: AppColors.surface,
          leading: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.asset(
                'assets/Belenergy ARG.webp',
                width: 80,
                height: 80,
                fit: BoxFit.contain,
              ),
            ),
          ),
          destinations: [
            const NavigationRailDestination(
              icon: Icon(Icons.dashboard_rounded),
              selectedIcon: Icon(Icons.dashboard_rounded),
              label: Text('Dashboard'),
            ),
            const NavigationRailDestination(
              icon: Icon(Icons.people_alt_rounded),
              selectedIcon: Icon(Icons.people_alt_rounded),
              label: Text('Clientes'),
            ),
            const NavigationRailDestination(
              icon: Icon(Icons.solar_power_rounded),
              selectedIcon: Icon(Icons.solar_power_rounded),
              label: Text('Productos'),
            ),
            const NavigationRailDestination(
              icon: Icon(Icons.receipt_long_rounded),
              selectedIcon: Icon(Icons.receipt_long_rounded),
              label: Text('Cotizaciones'),
            ),
            if (isAdmin)
              const NavigationRailDestination(
                icon: Icon(Icons.percent_rounded),
                selectedIcon: Icon(Icons.percent_rounded),
                label: Text('Descuentos'),
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
    final isAdmin = context.watch<AuthProvider>().isAdmin;
    final location = GoRouterState.of(context).matchedLocation;
    final selectedIndex = _currentTab(location, isAdmin);
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: (i) => _navigateTo(context, i),
        backgroundColor: AppColors.surface,
        indicatorColor: AppColors.primary.withOpacity(0.12),
        destinations: [
          const NavigationDestination(icon: Icon(Icons.dashboard_rounded), label: 'Dashboard'),
          const NavigationDestination(icon: Icon(Icons.people_alt_rounded), label: 'Clientes'),
          const NavigationDestination(icon: Icon(Icons.solar_power_rounded), label: 'Productos'),
          const NavigationDestination(icon: Icon(Icons.receipt_long_rounded), label: 'Cotizaciones'),
          if (isAdmin)
            const NavigationDestination(icon: Icon(Icons.percent_rounded), label: 'Descuentos'),
        ],
      ),
    );
  }
}
