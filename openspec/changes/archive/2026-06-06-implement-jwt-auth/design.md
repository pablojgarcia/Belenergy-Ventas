## Context

El backend actualmente carece de autenticación. Necesitamos una forma segura de autenticar usuarios (vendedores) y proteger el acceso a los datos de clientes en Odoo.

## Goals / Non-Goals

**Goals:**
- Implementar JWT para autenticación.
- Proteger rutas de API.
- Filtrar datos de Odoo por vendedor (usando email).

**Non-Goals:**
- Implementar un sistema completo de gestión de usuarios (registro, recuperación de contraseña). Se asumirá que los usuarios ya existen en el sistema.

## Decisions

- **JWT Library**: Se usará `jsonwebtoken` (o equivalente según el stack del proyecto).
- **Authentication Strategy**: Los vendedores se autenticarán enviando sus credenciales (asumido: email/contraseña), y el backend retornará un token JWT.
- **Middleware**: Un middleware interceptará las peticiones a `/customers` para verificar la validez del token y extraer el email del usuario.
- **Odoo Filter**: El servicio de Odoo utilizará el email extraído del token en el filtro de búsqueda (`domain`).

## Risks / Trade-offs

- **Risk**: Exposición de la clave secreta.
  - **Mitigation**: Utilizar variables de entorno para gestionar la clave secreta del JWT.
- **Risk**: Expansión del alcance.
  - **Mitigation**: Mantener la autenticación limitada solo a vendedores conocidos.
