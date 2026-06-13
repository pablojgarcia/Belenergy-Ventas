## Why

Los vendedores necesitan crear presupuestos (cotizaciones) desde la app y que se reflejen directamente en Odoo como `sale.order` en estado `draft`. Actualmente la pantalla "Crear presupuesto" existe pero solo muestra un snackbar local sin persistencia ni integración con Odoo.

## What Changes

- Nuevo endpoint `POST /orders/quotation` en el backend que recibe datos del presupuesto y crea un `sale.order` en Odoo vía `odoorpc`
- El endpoint persiste el presupuesto localmente en una nueva tabla `orders` con referencia al ID de Odoo
- La pantalla "Crear presupuesto" en Flutter se expande para incluir selección de productos con cantidades y precios
- Nuevo endpoint `GET /orders` para listar presupuestos del vendedor
- Nuevo endpoint `GET /orders/{id}` para ver detalle de un presupuesto

## Capabilities

### New Capabilities
- `create-quotation`: Crear cotización en Odoo desde la app con cliente, productos, cantidades y precios
- `list-quotations`: Listar presupuestos del vendedor autenticado
- `quotation-detail`: Ver detalle de un presupuesto individual

### Modified Capabilities
- *(ninguna)*

## Impact

- Backend: nuevo modelo `Order`, nuevos schemas Pydantic, nuevo endpoint, nuevo servicio Odoo para `sale.order`
- Frontend: refactor de `CrearPresupuestoScreen` para incluir selección de productos, nueva pantalla de listado de presupuestos
- Odoo: requiere que el usuario de integración tenga permisos para crear `sale.order`
