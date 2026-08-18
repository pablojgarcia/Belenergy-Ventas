import 'package:flutter/material.dart';
import '../utils/stock_semaphore.dart';
import '../utils/theme.dart';

/// Semáforo informativo de stock disponible (virtual_available de Odoo).
///
/// - `stock != null` → círculo verde/amarillo/rojo según
///   [resolveStockLevel], con tooltip del valor exacto.
/// - `stock == null` → estado "desconocido": círculo gris con "?", no bloquea
///   ninguna acción (el semáforo es informativo, no validación).
class StockSemaphoreIndicator extends StatelessWidget {
  final double? stock;
  final StockSemaphoreConfig config;

  const StockSemaphoreIndicator({super.key, this.stock, this.config = stockSemaphoreConfig});

  @override
  Widget build(BuildContext context) {
    final value = stock;
    if (value == null) {
      return const Tooltip(
        message: 'Stock desconocido',
        child: _StockDot(
          color: Color(0xFFC7C7CC),
          child: Text('?', style: TextStyle(fontSize: 8, fontWeight: FontWeight.w700, color: AppColors.textSecondary)),
        ),
      );
    }

    final color = switch (resolveStockLevel(value, config)) {
      StockLevel.red => AppColors.error,
      StockLevel.yellow => AppColors.warning,
      StockLevel.green => AppColors.success,
    };
    final formatted = value == value.roundToDouble()
        ? value.round().toString()
        : value.toStringAsFixed(2);

    return Tooltip(
      message: 'Stock disponible: $formatted',
      child: _StockDot(color: color),
    );
  }
}

class _StockDot extends StatelessWidget {
  final Color color;
  final Widget? child;

  const _StockDot({required this.color, this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 14,
      height: 14,
      decoration: BoxDecoration(shape: BoxShape.circle, color: color),
      alignment: Alignment.center,
      child: child,
    );
  }
}