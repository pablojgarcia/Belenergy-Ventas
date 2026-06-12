import 'package:go_router/go_router.dart';
import '../services/auth_provider.dart';
import '../screens/splash_screen.dart';
import '../screens/login_screen.dart';
import '../screens/home_screen.dart';
import '../screens/clientes_screen.dart';
import '../screens/productos_screen.dart';
import '../screens/crear_presupuesto_screen.dart';
import '../models/client_model.dart';

GoRouter createRouter(AuthProvider authProvider) {
  return GoRouter(
    refreshListenable: authProvider,
    initialLocation: '/splash',
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
      GoRoute(
        path: '/home',
        builder: (_, __) => const HomeScreen(),
      ),
      GoRoute(
        path: '/customers',
        builder: (_, __) => const ClientesScreen(),
      ),
      GoRoute(
        path: '/products',
        builder: (_, __) => const ProductosScreen(),
      ),
      GoRoute(
        path: '/budget/create',
        builder: (_, state) =>
            CrearPresupuestoScreen(client: state.extra as Client),
      ),
    ],
  );
}
