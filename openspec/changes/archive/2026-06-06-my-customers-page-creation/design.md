# Design: Implementación de página "Mis Clientes"

## Arquitectura de Filtrado
Para garantizar que cada vendedor solo acceda a su cartera, la lógica reside en el backend:

1.  **Backend (FastAPI)**:
    -   El endpoint `GET /customers` utiliza la dependencia `get_current_user` para identificar al vendedor.
    -   La consulta SQL (SQLAlchemy) filtra los registros donde `Customer.salesperson_id` coincide con el identificador del usuario autenticado.

2.  **Frontend (Flutter)**:
    -   La interfaz consumirá la lista sin necesidad de enviar parámetros de filtro, lo que hace la implementación frontend más ligera y segura.

## Seguridad
-   El filtrado en el backend impide que un usuario malintencionado pueda manipular la petición para obtener clientes de otros vendedores (vía parámetros en el query string).
-   Se requiere que la tabla `users` o el mapeo de identidad esté alineado con el `salesperson_id` de Odoo.

## Tareas Pendientes
- [ ] Crear el archivo `design.md` en el repositorio.
- [ ] Implementar la vista en Flutter para mostrar la lista (si procede).
- [ ] Validar que la sincronización de clientes traiga correctamente el `salesperson_id`.
