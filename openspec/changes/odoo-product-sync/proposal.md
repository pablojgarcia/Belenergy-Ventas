## Why

Actualmente no existe un catálogo de productos local que permita a los vendedores consultar precios, descripciones y disponibilidad de productos sin depender de una conexión directa a Odoo. La sincronización de productos es un prerrequisito para futuras funcionalidades como la creación de presupuestos y órdenes de venta desde el portal.

## What Changes

- Crear el modelo `Product` en SQLAlchemy para almacenar productos localmente.
- Implementar un servicio de sincronización (`sync_products`) que consuma datos de `product.template` desde Odoo via `odoorpc`.
- Agregar endpoint `POST /sync/products` para activar la sincronización manual.
- Agregar endpoint `GET /products` para consultar el catálogo local con filtros básicos.
- Agregar endpoint `GET /products/{id}` para ver detalle de un producto.

## Capabilities

### New Capabilities
- `product-sync`: Servicio de sincronización de productos desde Odoo a la base de datos local.
- `product-catalog`: API de consulta de catálogo de productos con filtros (categoría, búsqueda por nombre).

### Modified Capabilities
- `api-routes`: Se agregan nuevas rutas al backend existente.

## Non-Goals

- No se sincroniza stock/inventario (se puede agregar en una fase posterior).
- No se sincronizan imágenes de productos.
- No se implementa sincronización automática programada (solo manual por ahora).
- No se sincronizan precios por lista de precios ni por vendedor (solo precio de venta estándar).
- No se crea interfaz de usuario en Flutter para el catálogo (solo API backend).

## Impact

- Nuevo modelo `Product` en `Backend/app/models.py`.
- Nuevo schema `ProductCreate`/`ProductOut` en `Backend/app/schemas.py`.
- Nuevo servicio `sync_products` en `Backend/app/services/odoo_sync.py`.
- Nuevos endpoints en `Backend/app/main.py`.
- Nueva tabla `products` en PostgreSQL.
- Dependencias existentes (`odoorpc`) ya instaladas — no se requieren nuevas dependencias.

## Assumptions

- Los productos en Odoo se almacenan en `product.template` (no `product.product` con variantes).
- El campo `categ_id` es el identificador de categoría y el nombre se obtiene del tuple `(id, name)`.
- El precio de venta (`list_price`) y el costo (`standard_price`) son los valores estándar sin impuestos.
- Todos los productos activos (`active = True`) deben sincronizarse.
- Los productos son visibles para todos los vendedores (no hay restricción por vendedor).
