## Spec: JWT Auth Service

### Requirements
- El sistema debe tener una endpoint para recibir credenciales y devolver un token JWT.
- El token JWT debe contener el email del usuario en el payload.
- La firma del token debe usar una clave secreta configurada mediante variable de entorno.

### Implementation Details
- Endpoint: `/api/auth/login`
- HTTP Method: `POST`
- Payload: `{ "email": "...", "password": "..." }`
- Response: `{ "token": "..." }`
