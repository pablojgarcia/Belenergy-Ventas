## Context

La app genera cotizaciones como borradores (`quotation_drafts`) que luego se "generan" creando una orden de venta en Odoo (`sale.order`). Hoy el borrador exige un `customer_id` de la tabla local `customers` (poblada por sincronización desde `res.partner`). El feature de Leads (registro de clientes potenciales + aprobación + creación de partner) resultó redundante para el negocio y se elimina.

El flujo objetivo: el vendedor elige un cliente existente **o** registra uno nuevo (razón social + CUIT opcional) desde el mismo modal/panel de la cotización; al generar, el sistema crea el `res.partner` en Odoo, lo sincroniza a la base local y recién entonces crea la `sale.order`.

## Goals / Non-Goals

**Goals:**
- Permitir generar cotizaciones para clientes nuevos sin salir de la pantalla de cotización.
- Crear el cliente en Odoo y en la base local de forma atómica al generar la cotización.
- Validar el CUIT (formato + dígito verificador) y evitar duplicados (local y Odoo).
- Eliminar por completo el feature de Leads (código, rutas, tablas).

**Non-Goals:**
- Integración con el padrón de ARCA/AFIP (requiere certificado WSAA). Se documenta como follow-up.
- Edición de datos de contacto del cliente nuevo (email, teléfono, dirección) más allá de razón social y CUIT.
- Alta de clientes independiente del flujo de cotización (ej. desde la pantalla de clientes).

## Decisions

### 1. Cliente nuevo en el borrador: dos columnas dedicadas
Se agregan `new_client_name VARCHAR` y `new_client_vat VARCHAR` (nullable) a `quotation_drafts`. Cuando el borrador corresponde a un cliente nuevo, `customer_id` queda `NULL` y se usan estas columnas. Son dos campos tipados (sin JSONB) porque el MVP solo requiere razón social y CUIT.

### 2. Creación del cliente al generar
En `quotation_generation_service.generate()`:
1. Si `draft.customer_id is None` y `draft.new_client_name` está presente → crear cliente.
2. Si el CUIT provisto ya existe (local `customers.cuit` o `res.partner.vat` en Odoo) → `409` con mensaje claro ("Ya existe un cliente con ese CUIT"). El vendedor debe elegirlo desde el picker.
3. Validar CUIT con `utils/cuit.validar_cuit()` (formato 11 dígitos + mod-11); si es inválido → `400`.
4. Llamar `odoo_create_partner()` con `vendedor_externo = current_user.email` (mismo patrón que el lead, reutilizado) y hacer `upsert` en `customers`.
5. Asignar `draft.customer_id` y continuar con el flujo existente de `create_quotation()`.

El borrador debe seguir siendo editable (Guardar) sin `customer_id`, solo con `new_client_*`.

### 3. Reutilización del servicio de creación de cliente
Se extrae la lógica de `lead_service.create_partner` a un nuevo servicio `services/customer_creation_service.py` que recibe `db`, `user` y un dict con `{name, vat}` y devuelve el `Customer` local (creado vía `odoo_create_partner` + `CustomerRepository.upsert`). Queda disponible para futuras altas desde otros puntos de la app.

### 4. Validación CUIT
- `Backend/app/utils/cuit.py`: `validar_cuit(cuit: str) -> bool` — 11 dígitos + dígito verificador mod-11 (con las reglas de AFIP: resultado 11 → 0; resultado 10 → inválido).
- Frontend: espejo del validador para feedback inmediato; el backend es autoritativo.

### 5. Eliminación de Leads (completa)
- Se borran `api/leads.py`, `services/lead_service.py`, `repositories/lead_repository.py`, `integrations/odoo/crm_lead.py` y los schemas de lead.
- Se elimina el modelo `Lead` de `models.py` y su router de `main.py`.
- Migración Alembic `drop table leads` (**quita datos**). La tabla `leads` no se usa en producción con datos reales.
- `check_cuit_exists` se mueve a `integrations/odoo/partner.py` como `check_vat_exists`.
- Frontend: se borran las 4 pantallas de leads, rutas, destinos de navegación, quick item, tarjeta de stats y el botón admin "Aprobar leads", y los métodos de `api_service.dart`.
- Se archiva `openspec/changes/lead-management`.

### 6. API
- `POST /quotation-drafts` y `PUT /quotation-drafts/{id}` aceptan `customer_id` (nullable, como hoy) y opcionalmente `new_client_name` / `new_client_vat`.
- `POST /quotation-drafts/{id}/generate` queda igual en su contrato; el cambio es interno (crea el cliente antes de la orden si corresponde).
- No se agrega endpoint `POST /customers` en esta iteración.

## Risks / Trade-offs

- **Duplicados por nombre (sin CUIT)**: si el cliente no provee CUIT, no hay chequeo de duplicados posible; se puede crear un partner duplicado. Mitigación: el CUIT es opcional pero recomendado; si viene, el chequeo es estricto.
- **Creación en dos sistemas (Odoo + local) no transaccional**: si Odoo crea el partner pero la sincronización local falla, queda un partner huérfano. Se maneja con `try/except` y se reporta error claro; el siguiente sync de clientes reconciliará.
- **Drop de la tabla `leads`**: pérdida de datos de leads. Aceptado por el cliente (feature eliminado; datos de prueba).
- **Validación CUIT mod-11**: casos borde (prefijos 20/23/24/27 con resultado 10→9) se implementan según la especificación de AFIP; se cubren con tests.
