## Spec: API Protection Middleware

### Requirements
- Todas las rutas bajo `/api/customers` deben ser protegidas.
- El cliente debe enviar el token en el header `Authorization: Bearer <token>`.
- Si el token es inválido o falta, el backend debe retornar `401 Unauthorized`.
- Si el token es válido, debe extraer el email del usuario y adjuntarlo al objeto de la request (`req.user.email`).

### Implementation Details
- Middleware: `authMiddleware`
- Acción: Verifica firma del token y fecha de expiración.
