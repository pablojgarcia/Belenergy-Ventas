# Propuesta: Creación de la página "Mis Clientes"

## Objetivo de Negocio
Crear una nueva sección en el portal de ventas que permita a los vendedores visualizar únicamente los clientes que tienen asignados. Esto optimiza la gestión comercial y garantiza la seguridad de los datos al restringir el acceso a clientes no asignados.

## Metas
- Implementar una interfaz visual (UI) para listar clientes.
- Implementar la lógica de filtrado de seguridad en el backend para asegurar que cada vendedor solo acceda a su cartera de clientes.
- Consumir el endpoint filtrado desde el frontend (Flutter).

## No Metas
- Modificar datos de clientes desde el portal.
- Sincronizar clientes en tiempo real en esta vista.

## Suposiciones
- El endpoint `GET /customers` debe ser protegido y filtrar los resultados basándose en el usuario autenticado (usando `salesperson_id` asociado al usuario en el sistema).
- El sistema de autenticación ya inyecta el usuario actual en los endpoints protegidos.
