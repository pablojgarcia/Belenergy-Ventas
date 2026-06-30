import 'package:go_router/go_router.dart';
import '../services/auth_provider.dart';
import '../screens/splash_page.dart';
import '../screens/login_page.dart';
import '../screens/home_page.dart';
import '../screens/customers_page.dart';
import '../screens/products_page.dart';
import '../screens/create_quotation_page.dart';
import '../screens/quotations_page.dart';
import '../screens/quotation_detail_page.dart';
import '../screens/leads_page.dart';
import '../screens/create_lead_page.dart';
import '../screens/lead_detail_page.dart';
import '../screens/lead_approval_page.dart';
import '../widgets/responsive_shell.dart';

GoRouter createRouter(AuthProvider authProvider) {
  return GoRouter(
    refreshListenable: authProvider,
    initialLocation: '/splash',
    redirect: (context, state) {
      final isSplash = state.matchedLocation == '/splash';
      if (isSplash) return null;

      if (authProvider.status == AuthStatus.initial) {
        authProvider.checkAuthStatus();
        return null;
      }

      if (authProvider.status == AuthStatus.loading) {
        return null;
      }

      final isLoggedIn = authProvider.status == AuthStatus.authenticated;
      final isLogin = state.matchedLocation == '/login';

      if (!isLoggedIn && !isLogin) return '/login';
      if (isLoggedIn && isLogin) return '/';
      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (_, __) => const SplashPage(),
      ),
      GoRoute(
        path: '/login',
        builder: (_, __) => const LoginPage(),
      ),
      ShellRoute(
        builder: (_, __, child) => ResponsiveShell(child: child),
        routes: [
          GoRoute(
            path: '/',
            builder: (_, __) => const HomePage(),
          ),
          GoRoute(
            path: '/customers',
            builder: (_, __) => const CustomersPage(),
          ),
          GoRoute(
            path: '/products',
            builder: (_, __) => const ProductsPage(),
          ),
          GoRoute(
            path: '/quotations',
            builder: (_, __) => const QuotationsPage(),
            routes: [
              GoRoute(
                path: 'new',
                builder: (_, state) {
                  final customerId = state.uri.queryParameters['customer'];
                  return CreateQuotationPage(customerId: customerId);
                },
              ),
              GoRoute(
                path: ':id',
                builder: (_, state) => QuotationDetailPage(
                  itemId: state.pathParameters['id']!,
                ),
                routes: [
                  GoRoute(
                    path: 'edit',
                    builder: (_, state) => CreateQuotationPage(
                      draftId: state.pathParameters['id'],
                    ),
                  ),
                ],
              ),
            ],
          ),
          GoRoute(
            path: '/leads',
            builder: (_, __) => const LeadsPage(),
            routes: [
              GoRoute(
                path: 'approval',
                builder: (_, __) => const LeadApprovalPage(),
              ),
              GoRoute(
                path: 'new',
                builder: (_, __) => const CreateLeadPage(),
              ),
              GoRoute(
                path: ':id',
                builder: (_, state) => LeadDetailPage(
                  leadId: state.pathParameters['id']!,
                ),
                routes: [
                  GoRoute(
                    path: 'edit',
                    builder: (_, state) => CreateLeadPage(
                      leadId: state.pathParameters['id'],
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
