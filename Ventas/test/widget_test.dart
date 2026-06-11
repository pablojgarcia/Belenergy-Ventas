import 'package:flutter_test/flutter_test.dart';
import 'package:solarapp/main.dart';
import 'package:solarapp/services/auth_provider.dart';
import 'package:solarapp/config/router.dart';
import 'package:provider/provider.dart';

void main() {
  testWidgets('app renders MaterialApp', (tester) async {
    final authProvider = AuthProvider();
    final router = createRouter(authProvider);
    await tester.pumpWidget(SolarApp(router: router));
    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
