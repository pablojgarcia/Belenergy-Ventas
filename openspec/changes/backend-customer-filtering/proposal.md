## Por qué

Actualmente `GET /customers` devuelve TODOS los clientes de la base de datos y el frontend los filtra en memoria por el email del usuario logueado. Esto no es performante: a medida que crece la cartera de clientes, el frontend descarga miles de registros que no necesita, desperdiciando ancho de banda y memoria en dispositivos móviles.

## Qué cambia

**Solo backend** (no requiere cambios en frontend):

- Modificar `GET /customers` para filtrar por `salesperson_id` coincidente con `current_user.email` directamente en la consulta SQL
- Agregar fallback: también probar con `current_user.name` (el nombre visible desde Odoo) porque `salesperson_id` en la DB puede contener el email o el nombre según cómo lo sincronice Odoo
- El frontend sigue llamando al mismo endpoint y recibe solo sus clientes asignados

## Capacidades

### Modificadas
- `get-customers-endpoint`: `GET /customers` ahora retorna solo los clientes asignados al usuario autenticado

## Impacto

- Payload reducido y respuestas más rápidas para todos los usuarios
- No se requieren cambios en el frontend Flutter (el filtrado en `ClientesScreen` queda como redundante inofensivo)
- Compatible hacia atrás: el contrato de la API (forma de la respuesta) no cambia
