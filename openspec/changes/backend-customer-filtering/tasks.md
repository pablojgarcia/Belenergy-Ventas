## Backend

- [x] 1.1 Modificar `GET /customers` en `Backend/app/main.py` para filtrar por `current_user.email` y `current_user.name`
- [x] 1.2 Reiniciar backend y verificar que el endpoint devuelva solo los clientes asignados

## Frontend

- [x] 2.1 (Opcional) Eliminar el filtro redundante del lado cliente en `ClientesScreen._fetchClients()`

## Verificación

- [ ] 3.1 Iniciar sesión como vendedor y confirmar que `GET /customers` devuelva solo sus clientes
- [ ] 3.2 Iniciar sesión como otro vendedor y confirmar que vean un conjunto diferente (sin solapamiento)
- [ ] 3.3 Comparar tamaño de respuesta antes y después: confirmar que el payload es menor
