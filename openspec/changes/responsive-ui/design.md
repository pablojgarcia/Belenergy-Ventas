## Context

La app Flutter en `Ventas/` usa layouts fijos: `SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2)`, `StatCard` con width 140px, padding duros, y orientación portrait-locked. No hay `LayoutBuilder`, `MediaQuery` ni `OrientationBuilder` en ningún screen.

Al compilar a web, Android e iOS desde el mismo código, la falta de diseño responsive genera UX pobre en tablets (pantallas grandes con espacios desperdiciados) y web (contenido centrado o estirado sin aprovechar el ancho).

## Goals / Non-Goals

**Goals:**
- Crear un utilitario `Responsive` con breakpoints reutilizables (phone < 600, tablet < 1024, desktop >= 1024)
- Adaptar `HomeScreen`, `LoginScreen`, `ClientesScreen`, `ProductosScreen` al ancho de pantalla
- Adaptar `StatCard` y `MenuCard` para layouts dinámicos
- Desbloquear landscape en tablets/web; mantener portrait-lock en phone
- Mantener compatibilidad total con el código existente (no romper funcionalidad actual)

**Non-Goals:**
- No se cambia el backend ni la API
- No se agregan dependencias nuevas a Flutter
- No se modifica la lógica de negocio, autenticación, ni modelos
- No se implementa navegación con NavigationRail/Drawer persistente (fase futura)

## Decisions

| Decisión | Opción elegida | Alternativas consideradas | Razón |
|---|---|---|---|
| Breakpoints | `isPhone < 600`, `isTablet < 1024`, `isDesktop >= 1024` | Usar ` breakpoints` de Material3 | Los breakpoints estándar de Material Design son 600/840/1200; 600/1024 es más práctico para este dominio mobile-first |
| Implementación | Clase estática `Responsive` con extensiones en `BuildContext` | Provider o inherited widget | No necesita estado — es puramente derivado del `MediaQuery`. Una clase estática es suficiente y cero overhead |
| Orientación | `MediaQuery.of(context).size.shortestSide` para detectar phone | `Platform.isAndroid` / `kIsWeb` | El tamaño físico dicta la orientación, no la plataforma. Un tablet Android también debería poder rotar |
| Layout Clientes | Grid en tablets/desktop vs lista en phone | Usar `SliverGrid` responsive | Los clientes tienen datos densos; grid con 2-3 columnas en tablet/desktop aprovecha mejor el espacio |
| Layout Login | Card centrado con `maxWidth` en desktop | Mantener full-width actual | En pantallas grandes, un formulario centrado se ve más limpio y es más usabile |

## Risks / Trade-offs

- **[Riesgo] Rendimiento en web con grids grandes**: Flutter web renderiza con CanvasKit; grids con muchos elementos pueden ser lentos. → Usar `SliverGrid` con `SliverChildBuilderDelegate` (virtualización)
- **[Riesgo] Landscape en phone puede generar layouts rotos**: Algunos screens no están diseñados para landscape angosto. → Mantener portrait-lock solo en phones (shortestSide < 600)
- **[Trade-off] Un solo `Responsive` helper centralizado**: Menos boilerplate pero los widgets dependen de una única fuente de breakpoints. Si se necesitan breakpoints diferentes por screen, se puede sobrescribir localmente
