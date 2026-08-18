# Líneas de producto y motor de descuentos

## Cómo funcionan las líneas de producto

Las "líneas" (`product_lines`) son categorías comerciales propias de la app, ajenas a Odoo. Son 8 fijas:

| key | name |
|---|---|
| `deye` | Inversores Deye |
| `huawei` | Inversores Huawei |
| `sungrow` | Inversores Sungrow |
| `estructuras` | Estructuras / Fijación |
| `cables` | Cableado / Cables |
| `paneles_ja` | Paneles JA |
| `paneles_astro_575` | Paneles Astro 575 |
| `paneles_astro_615` | Paneles Astro 615 |

Se crean por seed al arrancar el backend (`Backend/app/seed_discount_rules.py:84-91`) y se gestionan desde la app en **Admin → Motor de descuentos → tab "Líneas de producto"** (`Ventas/lib/screens/admin_discount_rules_page.dart:441`).

## Cómo se asigna un producto a su línea (el rol de Odoo)

Odoo **no tiene** el concepto de línea; solo categorías de producto. El sync traduce categorías de Odoo → líneas en 3 pasos (`Backend/app/integrations/odoo/sync.py:206-227`):

1. **Recorrido del árbol de categorías hacia arriba**: desde la categoría del producto hacia la raíz, normaliza el nombre (sin acentos, minúsculas) y lo busca en `CATEGORY_ALIASES` (`sync.py:10-24`). La categoría hija gana sobre la padre.

   Estructura de categorías de Odoo esperada (según tests, `Backend/tests/test_product_line_resolver.py:4-19`):

   ```
   Goods
   ├── Inversores
   │   ├── DEYE        → deye
   │   ├── Huawei      → huawei
   │   └── Sungrow     → sungrow
   ├── Paneles Fotovoltaicos
   │   ├── JA          → paneles_ja
   │   ├── Astro 575   → paneles_astro_575
   │   └── Astro 615   → paneles_astro_615
   ├── Cableado        → cables
   ├── ACCESORIOS      → (no matchea) → paso 2
   └── Fijación        → estructuras
   ```

2. **Fallback por nombre del producto**: si ninguna categoría/ancestro matcheó, busca las palabras `deye`, `huawei`, `sungrow` en el nombre del producto (`BRAND_KEYWORDS`, `sync.py:26-30`). Así un "SDongle Huawei" colgado de "ACCESORIOS" cae en `huawei`.

3. Si nada matchea → `product_line_id = NULL` → **ese producto no tiene validación de descuento** (el motor le da `max_discount=None`, nunca bloquea — `discount_engine.py:66-86`).

El resultado se persiste en la BD local vía `POST /sync/products` (o el botón "Sincronizar productos" del home admin). Odoo nunca se entera de las líneas.

## Cómo lo interpreta el motor de descuentos

En la evaluación (`Backend/app/services/discount_engine.py:88-96`), cada producto de la cotización se filtra así:

```
seller_type (del usuario) + product_line_id (del PRODUCTO) + is_active
```

y de las reglas que matchean, se elige la primera cuyo tramo aplique:

- **Reglas `amount`** (todas menos paneles): tramo según el **total del presupuesto sin impuestos** (todas las líneas sumadas). Bandas: <500, <5k, <10k, <50k, >50k.
- **Reglas `qty`** (solo las 3 líneas de paneles, `QTY_CONDITION_LINES`, `discount_engine.py:8`): tramo según la **cantidad de esa línea individual** (medio pallet / pallet / 5 pallets / 10 pallets / container).
- Tramo: `min` inclusivo, `max` exclusivo (`_amount_matches`, `discount_engine.py:182-194`).

Si el descuento cargado supera el `max_discount` del tramo → `exceeded` → al generar la cotización se exige descripción de aprobación (`quotation_generation_service.py:118-130`). Líneas inactivas o `NULL` → sin validación.

## Operación diaria (checklist)

- **En Odoo** hay que cuidar las **categorías**: el nombre de la categoría (o la de algún ancestro) debe ser reconocible por `CATEGORY_ALIASES`. Si se crea una categoría nueva en Odoo para un inversor, su nombre tiene que contener "Deye/Huawei/Sungrow" o colgar de una categoría que matchee.
- **Después de crear/mover productos en Odoo**: correr "Sincronizar productos" para que se recalcule `product_line_id`.
- **Para agregar una línea nueva** (ej. "Baterías"): crear la línea en la UI admin, agregar su alias en `CATEGORY_ALIASES` (código), y armar las reglas de descuento por seller type y tramos en el tab "Reglas de descuento".

## Referencias en el código

| Aspecto | Ubicación |
|---|---|
| Motor de evaluación | `Backend/app/services/discount_engine.py` — `evaluate_lines()` (34-153) |
| Máximo y excedido | `discount_engine.py:120-121` |
| Resolución producto → línea | `Backend/app/integrations/odoo/sync.py:206-227` |
| CRUD de líneas (backend) | `Backend/app/api/discount_rules.py:93-144` |
| UI de líneas y reglas | `Ventas/lib/screens/admin_discount_rules_page.dart` |
| Seed de líneas y reglas | `Backend/app/seed_discount_rules.py` |
| Especificación comercial | `openspec/changes/discount-rules-engine/specs/discount_spec.md` |