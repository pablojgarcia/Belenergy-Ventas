import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'services/auth_provider.dart';
import 'services/api_service.dart';
import 'utils/theme.dart';
import 'config/router.dart';

import 'package:flutter_web_plugins/url_strategy.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  usePathUrlStrategy();

  final authProvider = AuthProvider();
  final router = createRouter(authProvider);

  runApp(
    MultiProvider(
      providers: [
        Provider(create: (_) {
          final api = ApiService();
          api.onAuthFailure = () {
            authProvider.logout();
          };
          return api;
        }),
        ChangeNotifierProvider.value(value: authProvider),
      ],
      child: SolarApp(router: router),
    ),
  );
}

class SolarApp extends StatefulWidget {
  final GoRouter router;

  const SolarApp({super.key, required this.router});

  @override
  State<SolarApp> createState() => _SolarAppState();
}

class _SolarAppState extends State<SolarApp> {
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'SolarApp',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      routerConfig: widget.router,
    );
  }
}
