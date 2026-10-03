## Why

El motor de descuentos devuelve "no tiene una regla de descuento aplicable" para
productos que sí tienen reglas cargadas. Es un bug de producción, no de
configuración: al agregar 501 unidades de un cable, y al vender
`MODULO BIFACIAL 144 CELDAS. CABLE TIPO N 575W 1,4M ASTRONERGY`, ambos
devolvieron `max_discount: null`.

La causa es un desajuste de tipos en la capa de caché. En
`discount_engine.py:73` se arma `rules_by_line` usando como clave
`rule.product_line_id`. Esa clave es un `uuid.UUID` cuando las reglas vienen de
la base (SQLAlchemy tipa la columna `Uuid`), pero es un `str` cuando vienen del
caché de Redis (el viaje por `json.dumps`/`json.loads` convierte los UUID en
strings). La línea 118 busca con `rules_by_line.get(product_line.id, [])`, donde
`product_line.id` **siempre** es un `uuid.UUID`. Por lo tanto la ruta del caché
nunca matchea: `rules` queda vacío, `_find_applicable_rule` devuelve `None`, y
la línea de producto cae en el mensaje de "requiere aprobación manual".

Como el TTL efectivo es `CACHE_DEFAULT_TTL` (60s por default), el patrón en
producción es: la **primera** evaluación después de que expira el caché acierta,
y **todas las siguientes dentro de la ventana de 60s fallan**. Eso lo hace
parecer intermitente y con datos faltantes, cuando en realidad el motor está
funcionando o no según si Redis tiene o no la respuesta.

Verificado en producción con el producto id 68 (`paneles_astro_575`, 106.375),
100 unidades, `representante_general`:

```
100 u con cache FRIO    : max=11.0  tier=qty [36–180]  msg=None
100 u con cache CALIENTE: max=None   tier=None          msg='...no tiene una regla aplicable...'
```

Con el caché desactivado el motor reproduce la planilla
`docs/politica de descuentos por linea.xlsx` **exactamente** en las seis bandas
de `paneles_astro_575`. Los valores del seed son correctos; lo roto es el caché.

El bug llegó a producción con la suite en verde porque `tests/conftest.py` no
levanta Redis: `get_redis()` devuelve `None`, `cache_get` devuelve `None`, y la
rama rota nunca se ejecuta en ningún test. Ningún test existente podía
reproducirlo.

## What Changes

- Restaurar los campos UUID al construir los objetos desde el caché en
  `DiscountEngine._get_cached_rules`, para que la ruta del caché devuelva
  objetos indistinguibles de los que devuelve la base.
- Agregar un test de regresión que falsifica Redis (en vez de omitirlo) y
  verifica que una evaluación con caché frío y otra con caché caliente dan el
  mismo resultado.
- Migrar los usuarios que quedaron con `seller_type = 'vendedor_interno'`, un
  valor que ya no existe en la matriz de descuentos. `admin` pasa a
  `["representante_general", "representante_agro"]`; los usuarios de prueba al
  default.
- Normalizar `vendedor_interno` a `representante_general` en `industry.py`, para
  que un dato obsoleto no vuelva a resolver a un seller_type sin reglas.
- Eliminar la clave `representante_general` duplicada en `QTY_RULES`.

## Capabilities

### New Capabilities
- `discount-engine-cache-transparency`: La capa de caché del motor de descuentos
  SHALL devolver objetos equivalentes a los de la base, de modo que el resultado
  de una evaluación no dependa de si Redis tiene o no la respuesta.

### Modified Capabilities
- (ninguna — `discount-rules-engine` describe la matriz de tramos y no cubre el
  comportamiento del caché ni la normalización de seller_type)

## Impact

- **Backend**: 2 archivos modificados
  - `Backend/app/services/discount_engine.py` (dentro de `_get_cached_rules`)
  - `Backend/app/integrations/odoo/industry.py` (`user_seller_types`,
    `principal_seller_type`)
  - `Backend/app/seed_discount_rules.py` (clave duplicada en `QTY_RULES`)
- **Migraciones**: 1 nueva
  - `Backend/alembic/versions/d3f4a5b6c7d8_fix_users_with_legacy_vendedor_interno.py`
    (`down_revision = a6b7c8d9e0f1`). Corrección de datos, idempotente: solo
    toca filas cuyo `seller_types` todavía menciona el valor legacy. Su
    `downgrade` es no-op a propósito, igual que `b4c5d6e7f8a9`: restaurar el
    valor devolvería a los usuarios al bug que la migración arregla.
- **Tests**: 1 archivo nuevo, 1 modificado
  - `Backend/tests/test_discount_rule_cache.py` (nuevo)
  - `Backend/tests/test_industry_mapping.py` (4 casos de normalización)
- **Frontend**: sin cambios
- **Dependencias**: sin cambios
- **Datos**: no hace falta purgar Redis, las claves tienen TTL de 60s y se
  regeneran solas. La migración de usuarios corre sola en el arranque
  (`app/main.py` corre `alembic upgrade head`).
- **API**: sin cambios en la forma de la respuesta

## Dato de contexto: por qué `vendedor_interno` quedó a medio migrar

El commit `477a88e` (2026-08-19, *"Eliminar seller type vendedor_interno de
reglas de descuento (default representante_general)"*) tomó una decisión clara:
los vendedores internos **no son un seller_type aparte, usan las reglas de
`representante_general`**. Por eso cambió los tres fallbacks de `industry.py` y
borró las reglas con `b4c5d6e7f8a9`.

Lo que no hizo fue migrar los datos de los usuarios. Y el fallback solo dispara
cuando `seller_types` viene vacío, así que `admin`, `Vendedor test` y `vendedor`
—que tenían `["vendedor_interno"]` guardado explícitamente— seguido resolviendo
a un seller_type sin reglas. Este change completa esa migración.

Dato relevante: **no se siembran reglas nuevas para `vendedor_interno`**, porque
eso iría contra una decisión ya tomada. La hoja `Vendedores Internos` de la
planilla es idéntica a `Representantes General` salvo Huawei >50.000 (15% vs
20%), diferencia que ya estaba marcada como `TODO` en `seed_discount_rules.py`
cuando se hizo el rename.

## Non-Goals

Este change arregla **el motor** y **los datos que dejaron al motor sin reglas**.
Queda explícitamente afuera, ya detectado al comparar el seed contra la planilla
y acordado con el usuario:

- **La banda `10k-50k`.** `BAND_MAP["amount"]["lt_10000"]` es `(5000, 50000)`,
  un rango que la planilla no define. Se deja como está: ya está documentado en
  `discount-rules-engine/specs/discount_spec.md:11` como decisión ("10k - 50k |
  mismo tramo 10k").
- **Reglas `kit` ausentes.** Documentado como inactivo en v1
  (`discount_spec.md:25`).
- **`container` en Astro 575/615.** La planilla ponía `-` pero el seed crea la
  regla. No se toca.
- **Docstring desactualizado** que dice TTL 300s cuando el efectivo es
  `CACHE_DEFAULT_TTL` (60s). No se toca.
- **`discount_rule_id` nunca expuesto**: el motor lo calcula pero
  `DiscountRuleResult` no tiene el campo, así que el schema lo descarta. No se
  toca.
- **Divergencia de industria entre endpoints**: `quotations.py:121` usa
  `principal_seller_type` (ignora la industria) mientras la generación real usa
  `effective_seller_type`. Con `admin` en `representante_general` +
  `representante_agro`, esto queda más visible: el preview del borrador puede
  mostrar 11% y la generación terminar en 5%. No se toca en este change.