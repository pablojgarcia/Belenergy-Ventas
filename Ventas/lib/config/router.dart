import 'package:go_router/go_router.dart';
import '../services/auth_provider.dart';
import '../screens/splash_screen.dart';
import '../screens/login_screen.dart';
import '../screens/home_screen.dart';
import '../screens/clientes_screen.dart';
import '../screens/productos_screen.dart';
import '../screens/crear_presupuesto_screen.dart';
import '../screens/presupuestos_screen.dart';
import '../screens/presupuesto_detalle_screen.dart';
import '../widgets/responsive_shell.dart';
import '../models/client_model.dart';
import '../utils/route_observer.dart';

GoRouter createRouter(AuthProvider authProvider) {
  return GoRouter(
    refreshListenable: authProvider,
    initialLocation: '/splash',
    observers: [routeObserver],
    redirect: (context, state) {
      final isSplash = state.matchedLocation == '/splash';
      if (isSplash) return null;

      if (authProvider.status == AuthStatus.initial ||
          authProvider.status == AuthStatus.loading) {
        return null;
      }

      final isLoggedIn = authProvider.status == AuthStatus.authenticated;
      final isLogin = state.matchedLocation == '/login';

      if (!isLoggedIn && !isLogin) return '/login';
      if (isLoggedIn && isLogin) return '/home';
      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (_, __) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (_, __) => const LoginScreen(),
      ),
      StatefulShellRoute.indexedStack(
        builder: (_, __, navigationShell) =>
            ResponsiveShell(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/home',
                builder: (_, __) => const HomeScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/customers',
                builder: (_, __) => const ClientesScreen(),
                routes: [
                  GoRoute(
                    path: 'budget/create',
                    builder: (_, state) => CrearPresupuestoScreen(
                      client: state.extra as Client,
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/products',
                builder: (_, __) => const ProductosScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/orders',
                builder: (_, __) => const PresupuestosScreen(),
                routes: [
                  GoRoute(
                    path: ':id',
                    builder: (_, state) => PresupuestoDetalleScreen(
                      orderId: int.parse(state.pathParameters['id']!),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    ],
  );
}
