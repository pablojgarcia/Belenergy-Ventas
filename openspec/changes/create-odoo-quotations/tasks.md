## 1. Backend: Modelo y esquemas

- [x] 1.1 Crear modelo `Order` en `models.py` con campos: `id`, `odoo_id`, `client_id`, `client_name`, `amount_total`, `state`, `date_order`, `user_id`
- [x] 1.2 Crear schemas `OrderCreate`, `OrderOut`, `OrderLineInput` en `schemas.py`

## 2. Backend: Servicio Odoo para sale.order

- [x] 2.1 Crear `services/odoo_sale.py` con función `create_quotation()` que crea `sale.order` y `sale.order.line` en Odoo con producto, cantidad, precio unitario, impuesto y descuento
- [x] 2.2 La función valida que el cliente exista en Odoo y el vendedor tenga permiso
- [x] 2.3 Calcular `amount_total` considerando subtotales, impuestos y descuentos

## 3. Backend: Endpoints REST

- [x] 3.1 Agregar `POST /orders/quotation` que recibe `partner_id`, `order_line` (lista de productos) y `description`, crea en Odoo y persiste localmente
- [x] 3.2 Agregar `GET /orders` que lista cotizaciones del vendedor autenticado, con filtro opcional por `state`
- [x] 3.3 Agregar `GET /orders/{id}` que devuelve detalle de cotización individual (incluye datos de Odoo)

## 4. Frontend: Pantalla de creación de presupuesto

- [x] 4.1 Refactor `CrearPresupuestoScreen` para mostrar selector de productos con cantidades y precios
- [x] 4.2 Conectar el formulario al endpoint `POST /orders/quotation`
- [x] 4.3 Mostrar confirmación y redirigir al listado tras creación exitosa

## 5. Frontend: Pantalla de listado de presupuestos

- [x] 5.1 Crear pantalla `PresupuestosScreen` que lista cotizaciones del vendedor
- [x] 5.2 Agregar filtro por estado (draft, sent, sale, cancel)
- [x] 5.3 Agregar ruta `/orders` en el router y enlace desde el menú principal

## 6. Frontend: Pantalla de detalle de presupuesto

- [x] 6.1 Crear pantalla de detalle que muestra información del cliente, líneas de producto y total
- [x] 6.2 Agregar ruta `/orders/{id}` y navegación desde el listado

## 7. Verificación

- [ ] 7.1 Probar creación de cotización en local con Docker
- [ ] 7.2 Verificar que la cotización aparece en Odoo como `draft`
- [ ] 7.3 Probar listado y detalle de cotizaciones
- [ ] 7.4 Probar casos de error (cliente no asignado, producto inexistente, Odoo caído)
