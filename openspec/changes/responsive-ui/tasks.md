## 1. Core responsive utility

- [x] 1.1 Crear `lib/utils/responsive.dart` con clase `Responsive` (breakpoints 600/1024, `isPhone`, `isTablet`, `isDesktop`, `value()`)
- [x] 1.2 Agregar extensión `BuildContext` en responsive.dart para acceso tipo `context.isPhone`

## 2. Conditional orientation

- [x] 2.1 En `main.dart`: reemplazar portrait-lock fijo por lógica condicional que detecte phone vs tablet/web usando `Responsive`

## 3. Refactor StatCard

- [x] 3.1 Eliminar `width: 140` fijo de `StatCard`, usar constraints del padre
- [x] 3.2 Verificar que `StatCard` se vea bien en cualquier ancho

## 4. Refactor MenuCard

- [x] 4.1 Hacer que padding, icon container y font sizes de `MenuCard` escalen proporcionalmente

## 5. Refactor HomeScreen

- [x] 5.1 Hacer que stats cards usen horizontal scroll en phone, 2-column grid en tablet, row wrapping en desktop
- [x] 5.2 Hacer que menu grid use 2 columnas en phone, 3 en tablet, 4 en desktop

## 6. Refactor LoginScreen

- [x] 6.1 Envolver el formulario en un `Center` con `ConstrainedBox(maxWidth: 400)` cuando sea tablet/desktop
- [x] 6.2 Mantener layout full-width actual en phone

## 7. Refactor ClientesScreen

- [x] 7.1 Cambiar `ListView` por `SliverGrid` con columnas variables según breakpoint
- [x] 7.2 Ajustar padding y tamaño de tarjetas para grid

## 8. Refactor ProductosScreen

- [x] 8.1 Hacer que el grid de productos use columnas adaptativas (1 phone, 2 tablet, 3 desktop)
