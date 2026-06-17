import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:solarapp/main.dart';
import 'package:solarapp/services/auth_provider.dart';
import 'package:solarapp/config/router.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('app starts and shows splash screen', (tester) async {
    final authProvider = AuthProvider();
    final router = createRouter(authProvider);
    await tester.pumpWidget(SolarApp(router: router));
    await tester.pump();

    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
