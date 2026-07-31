# Estado Actual de Belenergy-Ventas

Este documento detalla el estado funcional actual del repositorio de Belenergy-Ventas.

## Backend
- **Framework:** FastAPI (Python) con SQLAlchemy ORM.
- **Base de datos:** PostgreSQL en producción; SQLite en entornos de prueba.
- **Autenticación:** JWT con hashing de contraseñas y refresh tokens.
- **Clientes:** sincronización desde Odoo (`res.partner`) con asignación de vendedor.
- **Productos:** sincronización de productos e impuestos desde Odoo (lista de precios USD).
- **Cotizaciones:** borradores (`quotation_drafts`) con líneas de producto, generación de `sale.order` en Odoo y descarga de PDF (validado con magic bytes `%PDF-`).
- **Cliente nuevo:** alta de `res.partner` en Odoo al generar una cotización cuando el borrador usa `new_client_name`/`new_client_vat` (validación de CUIT mod-11 AFIP y anti-duplicados local/Odoo).
- **Leads:** feature eliminado por completo (endpoints, servicio, repositorio, integración Odoo CRM, tabla y migración de drop).

## Frontend
- **Framework:** Flutter (compatible con Web).
- **Pantallas:** login, dashboard, clientes, productos, cotizaciones (listado, creación/edición con modal de selección de cliente y panel de cliente nuevo, detalle con PDF).
- **Navegación:** `go_router` con `ResponsiveShell` (NavigationRail en escritorio, NavigationBar en móvil).
- **Estado:** Provider (`AuthProvider`, `ApiService`).

## Infraestructura
- **Backend:** Railway (FastAPI + migraciones Alembic vía `entrypoint.sh`).
- **Frontend:** Cloudflare Workers (build de Flutter web).
- **Odoo:** Odoo v19 Online como fuente de verdad comercial.
- **Contenedores:** Dockerfile en `Backend` y `docker-compose.yml` en la raíz.
