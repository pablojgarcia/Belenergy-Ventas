# Tareas de Implementación: Transparencia del caché en el motor de descuentos

## 1. Corrección del caché

- [x] 1.1 En `Backend/app/services/discount_engine.py`, dentro de `_get_cached_rules`, convertir `id` y `product_line_id` con `uuid.UUID(...)` al construir los `SimpleNamespace` desde el caché.
- [x] 1.2 Confirmado que la línea 118 (`rules_by_line.get(product_line.id, [])`) no necesita cambios: con 1.1 el lookup funciona en ambas rutas.
- [x] 1.3 Comentario en el código explicando que la conversión a `UUID` es obligatoria, para que nadie la simplifique a `str` más adelante.

## 2. Test de regresión del caché

- [x] 2.1 Crear `Backend/tests/test_discount_rule_cache.py`.
- [x] 2.2 Cliente Redis falso (`get`/`setex`/`delete`) con monkeypatch sobre `cache_service.get_redis`. No se puede omitir el caché: sin `REDIS_URL` la suite nunca entra a la rama rota.
- [x] 2.3 Datos: producto en `paneles_astro_575` y producto en `deye`, con reglas reales del seed.
- [x] 2.4 Test de la invariante estructural: `_get_cached_rules` devuelve reglas cuyo `product_line_id` es **igual** al `ProductLine.id` (mismo tipo y valor).
- [x] 2.5 Test del síntoma: dos `evaluate_lines` consecutivos dan respuestas idénticas, y la segunda (que lee del caché) devuelve el `max_discount` del tramo, no `None`.
- [x] 2.6 **Verificado en ambos sentidos**: los 4 tests pasan con el fix y fallan sin él (`assert None == 11.0`, el síntoma exacto de producción).

## 3. Usuarios con `seller_type` legacy

- [x] 3.1 Crear `Backend/alembic/versions/d3f4a5b6c7d8_fix_users_with_legacy_vendedor_interno.py` con `down_revision = a6b7c8d9e0f1`.
- [x] 3.2 Migración idempotente vía SQLAlchemy Core (sin casts `::`, que el repo no usa): `admin` → `["representante_general", "representante_agro"]`; el resto → `["representante_general"]`.
- [x] 3.3 `downgrade` no-op a propósito, igual que `b4c5d6e7f8a9`: restaurar el valor devolvería a los usuarios al bug.
- [x] 3.4 Verificar la migración ejecutándola contra una base de prueba: `admin` y `pablo` quedan iguales; `Vendedor test` y `vendedor` al default.
- [x] 3.5 Normalizar el valor legacy en `industry.py` (`_normalize`, aplicado en `user_seller_types` y `principal_seller_type`) para que no vuelva a resolver a un tipo sin reglas.
- [x] 3.6 Tests en `test_industry_mapping.py`: legacy solo, legacy mezclado con valores vigentes, no-regresión de los valores actuales, y `effective_seller_type` con el valor legacy.

## 4. Limpieza del seed

- [x] 4.1 Eliminar la clave `representante_general` duplicada en `QTY_RULES`. Era un rename mal hecho de `477a88e`: el bloque de `vendedor_interno` renombrado a `representante_general` chocó con el bloque de general que ya existía, y Python conservaba el último. Los dos bloques eran idénticos, así que la limpieza es lossless.

## 5. Verificación

- [x] 5.1 Suite completa: **191 pasan, 4 skipped, 2 fallos** — los 2 son los preexistentes de `tests/test_odoo_connection.py` (ambientales: pegan al Odoo de prueba que ya no existe).
- [ ] 5.2 Commit y push para desplegar.

## 6. Verificación en producción (post-deploy)

- [ ] 6.1 Evaluar el producto id 68 (`paneles_astro_575`) con 100 unidades, **dos veces seguidas** dentro de la ventana de TTL. Las dos deben devolver `max_discount=11.0` y `tier="qty [36–180]"`. Hoy la segunda devuelve `None`.
- [ ] 6.2 Evaluar 501 unidades del cable (id 549) con `admin`. Debe devolver `max_discount=11.0` (`amount [500–5000]`). Hoy devuelve `null`.
- [ ] 6.3 Confirmar que `admin` tiene `seller_types = ["representante_general", "representante_agro"]` y que le aparece el selector de industria.
- [ ] 6.4 Contrastar 6.1 contra la fila "Ventas por pallet → 11%" de la hoja `Representantes General` de `docs/politica de descuentos por linea.xlsx`.
- [ ] 6.5 No purgar Redis: las claves tienen TTL de 60s y se regeneran solas.

## 7. Follow-ups (fuera de alcance, para backlog)

- [ ] 7.1 Corregir el docstring de `_get_cached_rules`: dice TTL 300s pero el efectivo es `CACHE_DEFAULT_TTL` (60s), porque `cache_set` se llama sin `ttl`.
- [ ] 7.2 Unificar `quotations.py:121` con `effective_seller_type`: hoy el preview del borrador usa `principal_seller_type` (ignora la industria) mientras la generación real usa `effective_seller_type`. **Más visible ahora que `admin` tiene los dos tipos**: el preview puede mostrar 11% y la generación terminar en 5%.
- [ ] 7.3 Evaluar exponer `discount_rule_id`: el motor lo calcula pero `DiscountRuleResult` no declara el campo, así que el schema lo descarta en silencio.
- [ ] 7.4 Confirmar con el equipo el rango USD 10k-50k (la planilla no lo define) y el `container` de Astro 575/615 (la planilla ponía `-` pero el seed crea la regla).
- [ ] 7.5 Desambiguar `vendedor_interno`: hoy es a la vez el nombre de una persona (`users.vendedor_interno`, resuelto con `resolve_res_users_id_by_name`) y un seller_type que ya no existe. La colisión es la causa raíz de esta confusión.