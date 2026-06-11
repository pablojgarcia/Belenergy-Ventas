import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:solarapp/main.dart';
import 'package:solarapp/services/auth_provider.dart';
import 'package:solarapp/services/api_service.dart';
import 'package:solarapp/config/router.dart';
import 'package:provider/provider.dart';

void main() {
  testWidgets('app renders MaterialApp', (tester) async {
    final authProvider = AuthProvider();
    final router = createRouter(authProvider);
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          Provider(create: (_) => ApiService()),
          ChangeNotifierProvider.value(value: authProvider),
        ],
        child: SolarApp(router: router),
      ),
    );
    await tester.pump(const Duration(milliseconds: 1500));
    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
