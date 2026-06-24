# Gestión de Cotizaciones Integrada con Odoo

## Resumen

Implementar un flujo de cotizaciones donde PostgreSQL almacene borradores y referencias, mientras que Odoo continúa siendo la fuente de verdad para las cotizaciones oficiales.

La sincronización actual de clientes y productos desde Odoo hacia PostgreSQL ya existe y funciona correctamente. Esta especificación no modifica ese proceso.

## Objetivos

### Objetivo principal

Permitir que los vendedores:
- Creen borradores de cotización en la aplicación.
- Modifiquen borradores tantas veces como sea necesario.
- Generen una cotización oficial en Odoo cuando decidan enviarla.
- Consulten posteriormente las cotizaciones generadas.
- Descarguen el PDF oficial generado por Odoo.

### Fuera de alcance

- Sincronización de clientes (no modificar).
- Sincronización de productos (no modificar).
- Procesos batch existentes.
- Mecanismos actuales de autenticación.
- Lógica comercial de Odoo.
- Generación de PDF dentro de la aplicación (se descarga desde Odoo).

## Estado actual

Actualmente existen tablas `orders` y `order_lines` que serán reemplazadas por el nuevo modelo. También existe flujo de `vendedor_externo` que debe preservarse.

## Arquitectura objetivo

```
Flutter
   │
   ▼
FastAPI (Layered Architecture)
   │
   ├── api/            → Endpoints REST + validaciones
   ├── services/       → Reglas de negocio + orquestación
   ├── repositories/   → Acceso a datos (PostgreSQL)
   ├── integrations/   → Comunicación con Odoo
   │
   ├── PostgreSQL
   │      ├── quotation_drafts
   │      ├── quotation_draft_lines
   │      └── quotations
   │
   └── Odoo
          ├── sale.order
          ├── sale.order.line
          └── PDF (descargado vía report)

```

## Modelo de datos

Todos los IDs locales son **UUID v4**. Las referencias a Odoo usan `odoo_id` (Integer).

### quotation_drafts

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID PK | |
| customer_id | UUID FK → customers.id | |
| status | VARCHAR(20) | `draft`, `generated`, `failed` |
| notes | TEXT | |
| created_by | UUID FK → users.id | |
| updated_by | UUID FK → users.id | Último usuario que modificó |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |
| version | INTEGER DEFAULT 1 | Para optimistic locking |

### quotation_draft_lines

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID PK | |
| draft_id | UUID FK → quotation_drafts.id | |
| product_id | UUID FK → products.id | |
| product_odoo_id | INTEGER | Para validar precio al generar |
| quantity | NUMERIC(12,2) | |
| unit_price | NUMERIC(12,2) | Precio al momento de agregar |
| discount | NUMERIC(5,2) | Porcentaje |
| tax_id | INTEGER[] | Lista de odoo_ids de impuestos |
| tax_rate | NUMERIC(5,2) | Tasa combinada al momento de agregar |
| created_at | TIMESTAMP | |

### quotations

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID PK | |
| draft_id | UUID FK → quotation_drafts.id | |
| customer_id | UUID FK → customers.id | |
| amount_untaxed | NUMERIC(12,2) | |
| amount_tax | NUMERIC(12,2) | |
| amount_total | NUMERIC(12,2) | |
| odoo_sale_order_id | BIGINT | |
| odoo_sale_order_name | VARCHAR(100) | |
| created_by | UUID FK → users.id | |
| created_at | TIMESTAMP | |

## Reglas de negocio

- **RN-001**: Un borrador puede existir sin productos.
- **RN-002**: Un borrador puede modificarse ilimitadamente mientras `status = draft`.
- **RN-003**: Al generar: `quotation_drafts.status = generated` y se crea registro en `quotations`.
- **RN-004**: No se permite generar dos veces el mismo borrador (check `status`).
- **RN-005**: Para generar, el borrador debe tener `customer_id` no nulo.
- **RN-006**: Cada línea debe tener `quantity > 0`.
- **RN-007**: Cada producto debe tener `product_odoo_id` válido.
- **RN-008**: El cliente debe tener `odoo_id` válido.
- **RN-009**: La fuente de verdad de cotizaciones oficiales es Odoo.
- **RN-010**: No almacenar `sale.order` ni `sale.order.line` de Odoo localmente.
- **RN-011**: Al generar, validar que `unit_price` de cada línea coincida con el precio actual del producto en BD local. Si cambió, error: "El precio del producto {nombre} en la línea #{n} cambió. Recargue el borrador."
- **RN-012**: Si Odoo falla parcialmente (sale.order creado pero líneas no), el borrador queda `status = failed` con mensaje "Error al generar: reintente más tarde".

## Flujo de generación

1. Usuario presiona "Generar Cotización".
2. Backend valida: borrador existe, `status = draft`, cliente válido, líneas válidas.
3. Backend valida precios: compara `unit_price` de cada línea con `list_price` actual del producto. Si difieren, error.
4. Backend obtiene `vendedor_externo` del cliente y lo incluye en la creación en Odoo.
5. Backend computa `amount_untaxed`, `amount_tax` (usando `tax_rate` de cada línea) y `amount_total`.
6. Backend crea `sale.order` + `sale.order.line` en Odoo mediante `odoorpc`.
7. Si Odoo falla total o parcialmente → `draft.status = failed`, se retorna error 502, el usuario puede reintentar.
8. Si Odoo responde OK → se guarda `quotations`, se actualiza `draft.status = generated`.
9. Se retorna `{ "quotation_id", "odoo_sale_order_id", "odoo_sale_order_name" }`.

## API

### Drafts

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /quotation-drafts | Crear borrador vacío |
| GET | /quotation-drafts | Listar borradores (filtros: customer_id, status, created_by, q, date_from, date_to) |
| GET | /quotation-drafts/{id} | Obtener borrador con líneas |
| PUT | /quotation-drafts/{id} | Actualizar borrador (requiere `version` actual para optimistic locking) |
| DELETE | /quotation-drafts/{id} | Eliminar borrador (solo si `status = draft`) |
| POST | /quotation-drafts/{id}/generate | Generar cotización en Odoo |

### Quotations

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /quotations | Listar cotizaciones generadas (filtros: customer_id, date_from, date_to, q) |
| GET | /quotations/{id} | Obtener detalle |
| GET | /quotations/{id}/pdf | Descargar PDF desde Odoo (proxy: backend usa sesión odoorpc para obtener el report) |

## Arquitectura técnica (Refactor)

### api/
Routers FastAPI con dependencias de auth. Sin lógica de negocio.

### services/
- `DraftService`: CRUD de borradores con validaciones RN-001 a RN-008.
- `QuotationGenerationService`: Orquestación paso 1-9 del flujo de generación.
- `QuotationQueryService`: Consulta de cotizaciones generadas.
- `PdfService`: Obtiene PDF desde Odoo vía report proxy.

### repositories/
- `DraftRepository`: CRUD `quotation_drafts`.
- `DraftLineRepository`: CRUD `quotation_draft_lines`.
- `QuotationRepository`: CRUD `quotations`.
- `CustomerRepository`: Consulta `customers` (existe, se reusa).
- `ProductRepository`: Consulta `products` (existe, se reusa).

### integrations/odoo/
- `OdooClient`: Autenticación, crear `sale.order`, crear líneas, obtener PDF.
  - Creación: manejo de transacciones Odoo.
  - PDF: usa `ir.actions.report` + `report.download` con sesión odoorpc.
  - Manejo de errores RPC con timeout configurable.

## Optimistic Locking

Cada `PUT /quotation-drafts/{id}` debe incluir `version` en el body.
El backend:
```
actual = db.query(Draft).get(id)
if actual.version != request.version:
    raise 409 "El borrador fue modificado por otro usuario. Recargue e intente nuevamente."
actual.version += 1
```

## Manejo de errores

| Escenario | HTTP |
|-----------|------|
| Cliente inexistente | 404 |
| Producto inexistente | 404 |
| Borrador inexistente | 404 |
| Borrador ya generado | 409 |
| Conflictos de versión (optimistic lock) | 409 |
| Error de precio cambiado | 409 |
| Error Odoo | 502 |
| Timeout Odoo | 504 |

## Criterios de aceptación

- **CA-001**: Un vendedor puede crear un borrador y recuperarlo posteriormente.
- **CA-002**: Un vendedor puede modificar un borrador existente.
- **CA-003**: Un vendedor puede generar una cotización oficial en Odoo.
- **CA-004**: La generación crea un único `sale.order` en Odoo.
- **CA-005**: Las líneas se crean correctamente en Odoo con sus impuestos.
- **CA-006**: Se registra la referencia local de la cotización generada.
- **CA-007**: No existen copias locales completas de `sale.order`.
- **CA-008**: El PDF descargado corresponde al generado por Odoo.
- **CA-009**: La sincronización actual de clientes y productos continúa funcionando sin modificaciones.
- **CA-010**: Si el precio de un producto cambió, la generación falla con mensaje claro.
- **CA-011**: Si Odoo falla, el borrador queda en `failed` con posibilidad de reintentar.
- **CA-012**: Ediciones concurrentes detectadas (optimistic locking).
- **CA-013**: Se puede filtrar/buscar borradores y cotizaciones.

## Migración desde orders/order_lines

1. Se crean las nuevas tablas (`quotation_drafts`, `quotation_draft_lines`, `quotations`) con UUIDs.
2. Las tablas viejas `orders` y `order_lines` se eliminan (no hay datos productivos que migrar).
3. El refactor a layered architecture se hace antes de implementar la funcionalidad nueva.
