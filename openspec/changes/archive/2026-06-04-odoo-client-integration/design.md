# Design: Sincronización Odoo a Base de Datos Local

## Arquitectura
La sincronización seguirá un modelo **Pull-based** con persistencia local.

1.  **Backend (FastAPI)**: Servirá los datos desde PostgreSQL.
2.  **Base de Datos (SQLAlchemy)**: Almacenará los clientes con un campo `odoo_id` único para prevenir duplicados en cada sincronización.
3.  **Odoo Service (`odoorpc`)**: Módulo de servicio encargado de la comunicación vía XML-RPC.

## Flujo de Datos
1.  **Sincronización (Proceso de carga)**:
    -   El sistema consulta Odoo mediante `odoorpc` obteniendo los clientes necesarios.
    -   Se realiza un `Upsert` en la tabla `customers` local comparando el `odoo_id`.
2.  **Consulta (API)**:
    -   El frontend realiza un `GET /customers` contra el backend, el cual responde instantáneamente desde la base de datos local.

## Modelo de Datos (Esquema simplificado)
- `id` (PK, int)
- `odoo_id` (Unique, int)
- `name`, `email`, `phone`, `street`, `city`, `state`, `zip`, `country`, `vat`, `website` (str)
- `salesperson_id` (int)
