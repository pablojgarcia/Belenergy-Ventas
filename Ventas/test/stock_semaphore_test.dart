import 'package:flutter_test/flutter_test.dart';
import 'package:solarapp/utils/stock_semaphore.dart';

void main() {
  const defaultConfig = StockSemaphoreConfig();
  const customConfig = StockSemaphoreConfig(redMax: 2, yellowMax: 10);

  group('resolveStockLevel with default config', () {
    test('stock 0 es rojo (limite inclusivo)', () {
      expect(resolveStockLevel(0, defaultConfig), StockLevel.red);
    });

    test('stock negativo es rojo', () {
      expect(resolveStockLevel(-3, defaultConfig), StockLevel.red);
    });

    test('stock 1 es amarillo (limite inferior inclusivo)', () {
      expect(resolveStockLevel(1, defaultConfig), StockLevel.yellow);
    });

    test('stock 5 es amarillo (limite superior inclusivo)', () {
      expect(resolveStockLevel(5, defaultConfig), StockLevel.yellow);
    });

    test('stock decimal entre 1 y 5 es amarillo', () {
      expect(resolveStockLevel(2.5, defaultConfig), StockLevel.yellow);
    });

    test('stock 6 es verde', () {
      expect(resolveStockLevel(6, defaultConfig), StockLevel.green);
    });
  });

  group('resolveStockLevel with custom config (redMax=2, yellowMax=10)', () {
    test('stock 2 es rojo (redMax inclusivo)', () {
      expect(resolveStockLevel(2, customConfig), StockLevel.red);
    });

    test('stock 3 es amarillo', () {
      expect(resolveStockLevel(3, customConfig), StockLevel.yellow);
    });

    test('stock 10 es amarillo (yellowMax inclusivo)', () {
      expect(resolveStockLevel(10, customConfig), StockLevel.yellow);
    });

    test('stock 11 es verde', () {
      expect(resolveStockLevel(11, customConfig), StockLevel.green);
    });

    test('stock 0 con config custom sigue siendo rojo', () {
      expect(resolveStockLevel(0, customConfig), StockLevel.red);
    });
  });
}