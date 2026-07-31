## Why

Actualmente un vendedor solo puede generar cotizaciones para clientes que ya existen y fueron sincronizados desde Odoo. Cuando prospecta un cliente nuevo no tiene forma de cotizarle desde la app: debe registrarlo por otro canal (leads, WhatsApp, email) y esperar la carga manual en Odoo, generando demoras y pérdida de oportunidades. El flujo de leads resultó innecesario para el negocio y debe desaparecer.

## What Changes

- **Nueva cotización para clientes nuevos**: al presionar "Nueva cotización" el modal de clientes suma un botón **"Nuevo cliente"** que habilita un panel derecho editable con **Razón social** (obligatorio) y **CUIT** (opcional).
- **Creación del cliente al generar**: cuando el borrador pertenece a un cliente nuevo, al presionar "Generar cotización" se valida el CUIT, se crea el `res.partner` en Odoo, se sincroniza a la base local y se genera la orden de venta en un solo paso.
- **Validación de CUIT**: formato de 11 dígitos + dígito verificador (mod-11) en frontend y backend, con detección de duplicados (base local y Odoo) que devuelve un error claro en vez de crear duplicados.
- **Eliminación completa del feature de Leads** (**BREAKING**): se quitan pantallas, rutas, navegación, endpoints, servicio, repositorio, integración Odoo CRM y la tabla `leads` de la base de datos.
- La búsqueda de empresas en el padrón de **ARCA** queda documentada como follow-up (requiere certificado WSAA); en esta iteración el alta es manual con validación de CUIT.

## Capabilities

### New Capabilities
- `new-client-creation`: Alta de un cliente nuevo (creación en Odoo y sincronización local) desde el flujo de cotización, al momento de generar.
- `quotation-customer-selection`: Selección de cliente en "Nueva cotización" con botón "Nuevo cliente" y panel editable de razón social/CUIT.
- `cuit-validation`: Validación de CUIT (formato + dígito verificador) y prevención de duplicados contra clientes locales y Odoo.

### Modified Capabilities

<!-- No hay specs previas en openspec/specs/. La remoción de leads se documenta como breaking change en What Changes. -->

## Impact

- **Backend**: remoción del feature de leads (`api/leads.py`, `services/lead_service.py`, `repositories/lead_repository.py`, `integrations/odoo/crm_lead.py`, schemas de lead, modelo `Lead`, router y migración de drop de tabla). Nuevas columnas `new_client_name` y `new_client_vat` en `quotation_drafts`. Nuevo util `utils/cuit.py`. Modificación de `quotation_generation_service.py` para crear el cliente antes de la orden de venta.
- **Odoo Integration**: `create_partner()` en `integrations/odoo/partner.py` se reutiliza con `vendedor_externo = email del usuario`; se mueve `check_cuit_exists` a `partner.py` como `check_vat_exists`.
- **Frontend**: `create_quotation_page.dart` (botón "Nuevo cliente" + panel editable + payload con `new_client_*`). Remoción de pantallas, rutas y navegación de leads (`leads_page.dart`, `create_lead_page.dart`, `lead_detail_page.dart`, `lead_approval_page.dart`, `responsive_shell.dart`, `router.dart`, `home_page.dart`, `api_service.dart`).
- **Base de datos**: migración Alembic con drop de la tabla `leads` y columnas nuevas en `quotation_drafts`.
- **Docs**: actualización de `MANUAL.md`, `docs/current-state.md`, `docs/roadmap.md`, `docs/vision.md`, `docs/architecture.md`; archivo de `openspec/changes/lead-management`.
