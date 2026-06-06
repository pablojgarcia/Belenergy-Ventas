## Why

Actualmente, el backend no cuenta con un sistema de autenticación robusto para proteger los recursos. Implementar JWT permitirá asegurar los endpoints y personalizar el acceso a los datos de Odoo según el vendedor autenticado.

## What Changes

- Implementación de un servicio de autenticación para generar y validar JWT.
- Protección de endpoints de la API (ej: `/customers`) mediante middleware de verificación de JWT.
- Extracción del usuario del token para filtrar automáticamente las consultas a Odoo, garantizando que el vendedor solo vea sus clientes asociados.

## Capabilities

### New Capabilities
- `jwt-auth-service`: Servicio para emitir y verificar tokens JWT.
- `api-protection-middleware`: Middleware para proteger rutas y extraer información del usuario.

### Modified Capabilities
- `odoo-data-fetching`: Se modifica para integrar el filtrado dinámico basado en el email extraído del JWT.

## Impact

- Se requerirá un nuevo campo o configuración para la clave secreta del JWT.
- Se debe actualizar el cliente o las llamadas a los endpoints protegidos para enviar el token en el header `Authorization: Bearer <token>`.
- Los servicios que consumen Odoo deben ser adaptados para recibir el contexto del vendedor.
