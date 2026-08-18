import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:solarapp/models/industry_model.dart';
import 'package:solarapp/screens/create_quotation_page.dart';
import 'package:solarapp/services/api_service.dart';
import 'package:solarapp/widgets/stock_semaphore_indicator.dart';

class _FakeApi extends ApiService {
  _FakeApi({required this.products}) : super(overrideBaseUrl: 'http://test.local');

  final List<Map<String, dynamic>> products;

  @override
  Future<Map<String, dynamic>> getCustomer(int id) async {
    return {
      'id': id,
      'odoo_id': 10,
      'name': 'Cliente Test',
      'email': '',
      'phone': '',
      'company_name': '',
      'street': '',
      'city': '',
      'state': '',
      'zip': '',
      'country': '',
      'vat': '',
      'cuit': '',
      'vendedor_interno': '',
      'website': '',
      'industry': '',
    };
  }

  @override
  Future<List<Map<String, dynamic>>> getTermsAndConditions() async => [];

  @override
  Future<IndustryOptions> getIndustryOptions() async =>
      const IndustryOptions(showSelector: false, industries: []);

  @override
  Future<List<Map<String, dynamic>>> getProducts() async => products;

  @override
  Future<List<Map<String, dynamic>>> evaluateDiscountRules(
    List<Map<String, dynamic>> lines, {
    String? industry,
  }) async =>
      [];
}

Map<String, dynamic> _product(
  int id,
  String name, {
  double? virtualAvailable,
}) {
  return {
    'id': id,
    'odoo_id': id,
    'name': name,
    'default_code': 'P$id',
    'barcode': '',
    'list_price': 100.0,
    'taxes_id': <int>[],
    'virtual_available': virtualAvailable,
  };
}

Future<void> _pumpPage(WidgetTester tester, _FakeApi api) async {
  tester.view.physicalSize = const Size(2000, 1200);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);

  await tester.pumpWidget(
    MultiProvider(
      providers: [Provider<ApiService>(create: (_) => api)],
      child: const MaterialApp(
        home: CreateQuotationPage(customerId: '1'),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets(
      'el modal muestra el semaforo con el color del virtual_available '
      'recibido del JSON', (tester) async {
    final api = _FakeApi(products: [
      _product(1, 'Panel Verde', virtualAvailable: 20.0),
      _product(2, 'Panel Amarillo', virtualAvailable: 3.0),
      _product(3, 'Panel Sin Stock', virtualAvailable: 0.0),
    ]);

    await _pumpPage(tester, api);
    await tester.tap(find.text('Agregar producto'));
    await tester.pumpAndSettle();

    expect(find.byType(StockSemaphoreIndicator), findsNWidgets(3));

    Tooltip? tooltipOf(String message) {
      final candidates = tester
          .widgetList<Tooltip>(find.byType(Tooltip))
          .where((t) => t.message == message);
      return candidates.isEmpty ? null : candidates.first;
    }

    expect(tooltipOf('Stock disponible: 20'), isNotNull,
        reason: 'stock 20 deberia resolver a verde (limite superior)');
    expect(tooltipOf('Stock disponible: 3'), isNotNull,
        reason: 'stock 3 deberia resolver a amarillo');
    expect(tooltipOf('Stock desconocido'), isNull,
        reason: 'stock 0 no es desconocido, es rojo');

    final redDot = tester.widget<Container>(find.descendant(
      of: find.byWidgetPredicate(
          (w) => w is Tooltip && w.message == 'Stock disponible: 0'),
      matching: find.byType(Container),
    ));
    expect(redDot.decoration, isNotNull);
  });

  testWidgets(
      'un producto sin virtual_available (null) muestra estado desconocido '
      'y NO bloquea agregarlo', (tester) async {
    final api = _FakeApi(products: [
      _product(1, 'Panel Sin Dato', virtualAvailable: null),
    ]);

    await _pumpPage(tester, api);
    await tester.tap(find.text('Agregar producto'));
    await tester.pumpAndSettle();

    expect(find.byType(StockSemaphoreIndicator), findsOneWidget);

    final tooltips =
        tester.widgetList<Tooltip>(find.byType(Tooltip)).toList();
    expect(
        tooltips.any((t) => t.message == 'Stock desconocido'), isTrue,
        reason: 'sin dato de stock debe mostrar "?" gris, no asumir color');

    await tester.tap(find.text('Panel Sin Dato'));
    await tester.pumpAndSettle();

    expect(find.byType(Dialog), findsNothing,
        reason: 'el modal debe cerrarse y permitir agregar el producto');
    expect(find.text('Panel Sin Dato'), findsOneWidget,
        reason: 'el producto sin stock se agrega igual a la cotizacion');
  });
}