## Why

Actualmente, no existe una vista que permita a los usuarios visualizar la lista completa de clientes junto con la información relevante de su vendedor asignado. Esto dificulta el seguimiento comercial.

## What Changes

- Crear una nueva página 'my-customers' que consuma datos de la tabla 'customers' de PostgreSQL.
- La tabla mostrará: nombre del cliente y el nombre/email del vendedor (campo 'salesperson_id').

## Capabilities

### New Capabilities
- `customer-list-view`: Página para visualizar la lista de clientes con datos de su vendedor.

### Modified Capabilities
- 

## Impact

- Nueva ruta en la aplicación web para la página 'my-customers'.
- Consulta a la base de datos PostgreSQL para obtener la relación entre clientes y vendedores.
