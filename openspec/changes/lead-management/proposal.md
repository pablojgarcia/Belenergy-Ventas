## Why

Actualmente los vendedores externos solo pueden trabajar con clientes ya existentes sincronizados desde Odoo. No tienen forma de registrar un cliente potencial (lead) cuando prospectan un nuevo negocio. Esto obliga a los vendedores a utilizar canales externos (WhatsApp, email) para comunicar el potencial cliente al vendedor interno, quien debe crearlo manualmente en Odoo, generando demoras y pérdida de trazabilidad.

## What Changes

- Nuevo módulo de **Leads** que permite a vendedores externos registrar clientes potenciales desde la app.
- Flujo de aprobación: un lead pasa por estados `pendiente → aprobado → sincronizado` o `pendiente → rechazado`.
- Los vendedores internos (role `admin`) pueden ver, aprobar o rechazar leads desde el backend.
- Cuando un lead es aprobado, se crea el cliente en Odoo (`res.partner`) y se sincroniza automáticamente a la base local.
- Los leads siguen el mismo patrón de capas que las cotizaciones: API → Service → Repository → PostgreSQL.
- Se reusa la integración Odoo existente (`odoorpc`) para crear el `res.partner` en Odoo.
- Se agregan endpoints en el backend y pantallas en Flutter para la gestión de leads.
- Los vendedores externos pueden ver solo sus propios leads; los admins ven todos.

## Capabilities

### New Capabilities
- `lead-management`: Creación, edición y gestión de leads por vendedores externos.
- `lead-approval`: Flujo de aprobación/rechazo de leads por vendedores internos.
- `lead-odoo-sync`: Sincronización de leads aprobados a Odoo como `res.partner`.

### Modified Capabilities

<!-- Ninguna capacidad existente cambia sus requisitos a nivel de spec -->

## Impact

- **Backend**: Nuevo modelo `Lead` en `models.py`, nuevos schemas en `schemas.py`, nuevo router `api/leads.py`, nuevo servicio `services/lead_service.py`, nuevo repositorio `repositories/lead_repository.py`.
- **Odoo Integration**: Nueva función `create_customer()` en `integrations/odoo/partner.py` para crear `res.partner` en Odoo.
- **Frontend**: Nuevas pantallas en Flutter: lista de leads, creación de lead, detalle de lead, panel de aprobación.
- **Base de datos**: Nueva tabla `leads` y migración Alembic.
- **Sin impacto** en sincronización existente de clientes, productos, impuestos ni cotizaciones.
