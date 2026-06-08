## Context

El sistema sincroniza clientes desde Odoo a PostgreSQL. Cada cliente tiene un campo `salesperson_id` (email del vendedor asignado). El frontend filtra localmente por el email del usuario autenticado.

## Goals / Non-Goals

**Goals:**
- Mostrar al vendedor solo los clientes que tiene asignados en Odoo.
- Permitir crear presupuestos desde la lista de clientes.

**Non-Goals:**
- No se realizarán cambios en el esquema de base de datos existente.
- No se implementarán funciones de edición o creación de clientes.

## Decisions

- El filtrado se realiza en el frontend comparando `salespersonEmail` del cliente con `email` del usuario logueado.
- A futuro el filtrado puede moverse al backend por seguridad.

## Risks / Trade-offs

- [Risk] Posible latencia al consultar un gran volumen de clientes. → Mitigación: Implementar paginación en el listado.
