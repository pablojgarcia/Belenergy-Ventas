## Context

Actualmente la app tiene una pantalla "Crear presupuesto" que recibe un cliente y muestra un formulario con descripción y monto, pero al enviar solo muestra un snackbar sin persistencia. No hay modelo de datos local para órdenes ni integración con Odoo para crear `sale.order`.

## Goals / Non-Goals

**Goals:**
- Crear cotizaciones en Odoo (`sale.order`, estado `draft`) desde la app
- Persistir una referencia local de cada cotización con su ID de Odoo
- Listar cotizaciones del vendedor autenticado
- Ver detalle de una cotización

**Non-Goals:**
- No se editan ni cancelan cotizaciones desde la app (en MVP)
- No se sincronizan cotizaciones desde Odoo hacia la app
- No se manejan pagos ni facturación

## Decisions

### 1. Creación en Odoo primero, luego persistencia local
Se crea el `sale.order` en Odoo primero y se persiste localmente con el `odoo_id` devuelto. Esto evita estados huérfanos (orden local sin contraparte en Odoo).

### 2. Modelo `Order` local con campos mínimos
La tabla local almacena solo los campos necesarios para el listado y la referencia a Odoo: `id`, `odoo_id`, `client_id`, `client_name`, `amount_total`, `state`, `date_order`, `user_id`. El detalle completo se obtiene de Odoo.

### 3. Endpoint POST /orders/quotation recibe lista de productos
El body incluye `partner_id` (Odoo ID del cliente), `order_line` (lista de `{product_id, product_name, quantity, price_unit, tax_id, discount}`) y `description`. No se usa el modelo local de productos sino los IDs de Odoo directamente para evitar desincronización. El backend calcula el `amount_total` sumando subtotales con impuestos y descuentos.

### 4. Uso de odoorpc existente para crear sale.order
Se reutiliza `get_odoo_connection()` del módulo `odoo_sync.py`. Se crea un nuevo archivo `odoo_sale.py` para las operaciones de ventas.

### 5. Seguridad: solo el vendedor asignado puede crear cotizaciones para un cliente
El endpoint verifica que `customer.salesperson_id` coincida con el email o nombre del usuario autenticado.

## Risks / Trade-offs

- **Campos de Odoo cambian en diferentes versiones** → El endpoint mapea explícitamente los campos requeridos de `sale.order`. Si Odoo cambia la API, falla al crear.
- **El usuario de integración necesita permisos en Odoo** → Debe tener permisos de creación en `sale.order` y `sale.order.line`. Si no, la creación falla con error RPC.
- **Sin validación de stock** → La app no verifica disponibilidad de productos antes de crear la cotización.
