## Why

La app Flutter compila actualmente a web, Android e iOS desde un mismo código base, pero usa layouts fijos (anchos duros, grid de 2 columnas, portrait-locked) que no se adaptan al tamaño de pantalla. Esto genera una experiencia subóptima en tablets y web. Se necesita un sistema responsive que haga que la misma app se vea bien en cualquier dispositivo.

## What Changes

- Crear utilitario `Responsive` con breakpoints (phone/tablet/desktop) y métodos de valores adaptativos
- Desbloquear orientación landscape en tablets/web (mantener portrait-lock en phone)
- Refactorizar `HomeScreen` para que stats y menú grid se adapten al ancho de pantalla
- Refactorizar `LoginScreen` para mostrar formulario centrado en card en tablets/desktop
- Refactorizar `ClientesScreen` para usar grid en tablets/desktop en lugar de lista lineal
- Refactorizar `ProductosScreen` para usar grid responsive
- Refactorizar `StatCard` para que su ancho sea dinámico (no fijo 140px)
- Refactorizar `MenuCard` para adaptarse a diferentes tamaños de grid

## Capabilities

### New Capabilities
- `responsive-ui-system`: Sistema de diseño responsive con breakpoints, orientación condicional y widgets adaptativos para toda la app

### Modified Capabilities
- (ninguna — no hay specs existentes)

## Impact

- **Frontend**: 8 archivos modificados/creados en `Ventas/lib/`
  - Nuevo: `lib/utils/responsive.dart`
  - Modificados: `main.dart`, `home_screen.dart`, `login_screen.dart`, `clientes_screen.dart`, `productos_screen.dart`, `stat_card.dart`, `menu_card.dart`
- **Backend**: sin cambios
- **Dependencias**: sin cambios (todo es Flutter nativo, no requiere nuevos paquetes)
