## ADDED Requirements

### Requirement: Crear cotización en Odoo
El sistema DEBE permitir crear una cotización (`sale.order`) en Odoo en estado `draft` desde la app. La cotización puede contener 1 o más productos, sin restricción de cantidad.

Cada línea de producto DEBE incluir: producto, cantidad, precio unitario, impuesto (ID de Odoo) y descuento porcentual.
El sistema DEBE calcular el `amount_total` como suma de subtotales (cantidad × precio_unitario) más impuestos, menos descuentos.

#### Scenario: Creación exitosa con un producto
- **WHEN** el vendedor completa el formulario con cliente, un producto con cantidad 2, precio unitario $1000, IVA 21% y descuento 10%
- **THEN** el sistema crea un `sale.order` en Odoo con estado `draft` con `amount_total` = $2178 (2000 - 200 desc + 378 IVA) y devuelve el ID de Odoo

#### Scenario: Creación exitosa con múltiples productos
- **WHEN** el vendedor completa el formulario con cliente y 3 productos con diferentes cantidades, precios, impuestos y descuentos
- **THEN** el sistema crea un `sale.order` en Odoo con estado `draft` con todas las líneas y el total calculado correctamente

#### Scenario: Cliente no asignado al vendedor
- **WHEN** el vendedor intenta crear una cotización para un cliente que no le pertenece
- **THEN** el sistema rechaza la operación con error 403

#### Scenario: Producto inexistente en Odoo
- **WHEN** el vendedor envía un `product_id` que no existe en Odoo
- **THEN** el sistema rechaza la operación con error 400

#### Scenario: Error de conexión con Odoo
- **WHEN** Odoo no está disponible
- **THEN** el sistema responde con error 502 y no persiste nada localmente

### Requirement: Persistencia local de la cotización
El sistema DEBE guardar una referencia local de cada cotización creada con su ID de Odoo.

#### Scenario: Referencia guardada tras creación
- **WHEN** la cotización se crea exitosamente en Odoo
- **THEN** el sistema guarda un registro en la tabla `orders` con `odoo_id`, `client_id`, `amount_total`, `state`, `date_order` y `user_id`
