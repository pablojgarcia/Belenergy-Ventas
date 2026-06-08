# Tareas de Implementación: Odoo-Backend Integration

## Fase 1: Preparación
- [x] Configurar variables de entorno (`ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD`).
- [x] Instalar `odoorpc` en `requirements.txt`.

## Fase 2: Modelo de Datos
- [x] Crear/Actualizar el modelo `Customer` en `Backend/app/models/customer.py` con los campos definidos.
- [x] Ejecutar migraciones (`alembic revision --autogenerate`).

## Fase 3: Servicio Odoo
- [x] Implementar `Backend/app/services/odoo_sync.py` con la lógica de conexión y `upsert` de datos.

## Fase 4: API & Exposición
- [x] Implementar endpoint `GET /customers` para listar los datos locales.
- [x] Implementar endpoint `POST /sync/customers` para forzar la sincronización manual.

## Fase 5: Verificación
- [x] Probar la sincronización con un entorno de desarrollo de Odoo.
- [x] Verificar la respuesta de la API local.
