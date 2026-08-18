enum StockLevel { red, yellow, green }

/// Umbrales configurables del semáforo de stock.
///
/// rojo:   stock <= redMax
/// amarillo: redMax < stock <= yellowMax
/// verde:  stock > yellowMax
class StockSemaphoreConfig {
  final int redMax;
  final int yellowMax;

  const StockSemaphoreConfig({this.redMax = 0, this.yellowMax = 5});
}

/// Único punto de configuración de los umbrales del semáforo.
/// Cambiar acá afecta toda la app sin tocar widgets ni consultas.
const stockSemaphoreConfig = StockSemaphoreConfig();

StockLevel resolveStockLevel(num stock, StockSemaphoreConfig config) {
  if (stock <= config.redMax) return StockLevel.red;
  if (stock <= config.yellowMax) return StockLevel.yellow;
  return StockLevel.green;
}