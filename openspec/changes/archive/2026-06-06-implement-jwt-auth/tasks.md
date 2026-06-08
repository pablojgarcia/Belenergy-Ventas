## Tasks

- [x] Implementar endpoint de login `/api/auth/login` y generación de JWT.
- [x] Implementar middleware de autenticación `authMiddleware` para verificar JWT.
- [x] Proteger rutas `/api/customers` con el nuevo middleware.
- [x] Modificar servicio de consulta a Odoo para filtrar por `email` del usuario autenticado (extraído de `req.user.email`).
- [x] Configurar variable de entorno `JWT_SECRET` y asegurar su uso.
- [x] Validar flujos de error (token inválido, usuario no autorizado).
