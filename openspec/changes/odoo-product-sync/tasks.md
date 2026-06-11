# Tareas de Implementación: Sincronización de Productos Odoo

## Fase 1: Modelo de Datos

- [x] Explorar Odoo `product.template` para confirmar campos disponibles (ejecutar script de discovery).
- [x] Agregar modelo `Product` en `Backend/app/models.py`.
- [x] Agregar schemas `ProductBase`, `ProductCreate`, `ProductOut` en `Backend/app/schemas.py`.

## Fase 2: Servicio de Sincronización

- [x] Implementar función `sync_products(db)` en `Backend/app/services/odoo_sync.py`:
  - Conexión a Odoo (reutilizar `get_odoo_connection()`).
  - Consulta a `product.template` con filtro `[('active', '=', True)]`.
  - Mapeo de campos (incluyendo resolución de `categ_id` y `uom_id` como nombres).
  - Lógica de upsert por `odoo_id`.

## Fase 3: API & Endpoints

- [x] Agregar endpoint `POST /sync/products` en `Backend/app/main.py`.
- [x] Agregar endpoint `GET /products` en `Backend/app/main.py` con filtros opcionales.
- [x] Agregar endpoint `GET /products/{id}` en `Backend/app/main.py`.

## Fase 4: Verificación

- [x] Probar sincronización manual contra Odoo de prueba.
- [x] Verificar respuesta de `GET /products`.
- [x] Verificar upsert (segunda sincronización no debe crear duplicados).
- [x] Verificar filtros de búsqueda y categoría.
