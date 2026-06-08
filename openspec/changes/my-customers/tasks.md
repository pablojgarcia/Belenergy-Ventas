## 1. Backend (Ya implementado)

- [x] 1.1 Endpoint `GET /customers` existente con filtro por `salesperson_id`
- [x] 1.2 Sincronización desde Odoo con campo `salesperson_id` mapeado

## 2. Frontend

- [x] 2.1 Pantalla `ClientesScreen` creada con listado de clientes
- [x] 2.2 Filtrado por email del vendedor logueado implementado
- [ ] 2.3 Mejorar UI de la tarjeta de cliente (estados de carga, error, vacío)
- [ ] 2.4 Agregar paginación para volumen grande de clientes

## 3. Verification

- [ ] 3.1 Verificar que el `salesperson_id` de Odoo coincida con el email del usuario local
- [ ] 3.2 Probar flujo completo: login → ver solo mis clientes → crear presupuesto
