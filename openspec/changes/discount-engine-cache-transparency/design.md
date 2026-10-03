## Context

`DiscountEngine` carga las reglas de descuento de dos maneras: desde la base
(o cuando el caché expiró) o desde Redis. El objetivo de la caché es evitar una
consulta por evaluación, y eso funciona. El problema es que las dos rutas no
devuelven objetos del mismo tipo.

En `evaluate_lines` (`discount_engine.py:70-73`):

```python
rules_by_line: dict = {}
if line_ids:
    for rule in self._get_cached_rules(seller_type, line_ids):
        rules_by_line.setdefault(rule.product_line_id, []).append(rule)
```

`rule.product_line_id` depende de dónde venga la regla:

| Origen | Tipo de `rule.product_line_id` | Por qué |
|---|---|---|
| Base de datos | `uuid.UUID` | `DiscountRule.product_line_id` es `Column(Uuid)` (`models.py:226`) |
| Caché Redis | `str` | `cache_set` serializa con `json.dumps` y el UUID se vuelve string (`cache_service.py:56`) |

Y el lookup (línea 118) siempre usa el UUID:

```python
rules = rules_by_line.get(product_line.id, [])   # product_line.id es UUID
```

`uuid.UUID('8a9e...') != '8a9e...'`, así que en la ruta del caché el `.get`
siempre devuelve `[]`. De ahí `applicable is None` y el mensaje de "requiere
aprobación manual".

Medido en producción:

```
tipo de las claves de rules_by_line (BD)    : UUID
tipo de las claves de rules_by_line (cache) : str
product_line.id                             : UUID
pl.id == clave del cache                    : False
```

Vale notar que el filtro de la línea 197-201 del caché **sí** funciona, porque
compara strings: `str(r.get("product_line_id")) in wanted`. El bug no es de
filtrado, es de la clave del diccionario que se arma después. Por eso
`_get_cached_rules` devuelve las 10 reglas correctas y el resultado sigue
siendo `None`: las reglas están, pero indexadas bajo otra clave.

## Goals / Non-Goals

**Goals:**
- Que el resultado de `evaluate_lines` no dependa de si el caché está frío o
  caliente.
- Que el caché sea **transparente**: los objetos que devuelve la rama del caché
  deben ser indistinguibles de los que devuelve la rama de la base.
- Cubrir el bug con un test que pueda reproducirlo.

**Non-Goals:**
- No cambiar la matriz de tramos ni los valores del seed.
- No tocar el TTL ni el esquema de claves del caché.
- No agregar reglas que hoy no existen (`vendedor_interno`, `kit`).
- No unificar `quotations.py` con `effective_seller_type`.

## Decisiones

### D1: Restaurar los UUID en el caché, en vez de normalizar a `str`

Dos formas posibles de arreglar el desajuste:

**A. Tipar correctamente los objetos del caché** (elegida). Al construir los
`SimpleNamespace`, convertir `id` y `product_line_id` con `uuid.UUID(...)`. La
línea 118 no se toca.

**B. Normalizar las claves a `str`** en la línea 73 y en la 118.

Se elige A porque el contrato correcto de una capa de caché es ser
transparente: quien consume `_get_cached_rules` no debería poder distinguir de
dónde vinieron los datos. Con B el bug desaparece hoy, pero deja objetos con
campos de tipo incorrecto (`product_line_id` siendo `str` cuando el modelo
declara `Uuid`), que es exactamente la trampa que causó este bug. Cualquier
código futuro que use `rule.product_line_id` para comparar contra
`product_line.id` vuelve a romper igual, y esta vez sin que nadie entienda por
qué.

Además B obliga a tocar las dos líneas que participan del contrato, mientras
que A toca un solo punto de construcción y hace que el resto del motor siga
leyendo como si no hubiera caché — que es justamente lo que queríamos.

`uuid` ya está importado en `discount_engine.py:1`, así que no hay dependencia
nueva.

### D2: El test tiene que falsificar Redis, no omitirlo

`tests/conftest.py` no configura `REDIS_URL`, así que en la suite
`get_redis()` devuelve `None`, `cache_get` devuelve `None`, y la rama rota
**nunca se ejecuta**. Un test que solo llame a `evaluate_lines` pasaría con el
bug presente: por eso se desplegó con 183 tests en verde.

Hay dos formas de exercise el caché:

- Monkeypatchear `cache_service.cache_get`/`cache_set` con un dict en memoria.
- Monkeypatchear `cache_service.get_redis` con un fake que implemente
  `get`/`setex`, dejando que el viaje por `json.dumps`/`json.loads` ocurra.

Se elige la segunda. El `str` no aparece por una decisión del código del motor
sino por la serialización de Redis; falsear solo `cache_get` se saltearía
justamente el paso donde nace el bug, y el test volvería a ser incapaz de
detectarlo.

### D3: El assert es de igualdad entre frío y caliente, no de valor absoluto

El bug no se manifiesta como un valor incorrecto sino como una **diferencia**
entre la primera evaluación y la segunda. Por eso el test principal compara las
dos: `resultado_call_1 == resultado_call_2`. Un assert del estilo "100 unidades
devuelve 11%" passes hoy en verde con caché frío y en rojo con caché caliente, y
no documenta la invariante que realmente importa.

Se agrega además un assert explícito de la invariante estructural: que
`_get_cached_rules` devuelva reglas cuyo `product_line_id` sea **igual** al
`ProductLine.id` (mismo tipo y mismo valor). Ese es el contrato que hoy se
rompe, y localiza el fallo en el motor en vez de en el síntoma.

## Verificación

En producción, después del deploy, sobre el producto id 68
(`paneles_astro_575`), 100 unidades, `representante_general`:

```
100 u con cache FRIO    : max=11.0  tier=qty [36–180]  msg=None
100 u con cache CALIENTE: max=11.0  tier=qty [36–180]  msg=None
```

Ambas iguales, y coincide con la fila "Ventas por pallet → 11%" de la hoja
`Representantes General` de `docs/politica de descuentos por linea.xlsx`.

No hace falta purgar Redis: las claves tienen TTL de 60s y se regeneran solas.

**Advertencia:** el caso de los cables **sigue devolviendo `null` después de este
fix**, porque `admin`, `Vendedor test` y `vendedor` tienen
`seller_type='vendedor_interno'` y no existe ninguna regla para ese tipo. Este
change arregla el motor, no esa falta de reglas.