## Context

Actualmente los clientes solo se crean en Odoo y se sincronizan al portal. Los vendedores externos no tienen forma de registrar nuevos prospectos desde la app. Este diseño extiende la arquitectura existente de cotizaciones para soportar el flujo completo de leads: creación por vendedor externo, aprobación por vendedor interno, y creación del cliente en Odoo.

El diseño se basa en el patrón establecido de capas: API → Service → Repository → PostgreSQL, con integración Odoo vía `odoorpc`.

## Goals / Non-Goals

**Goals:**
- Permitir a vendedores externos crear leads con datos del cliente potencial.
- Proveer un flujo de aprobación/rechazo por vendedores internos (role `admin`).
- Sincronizar leads aprobados a Odoo como `res.partner`.
- Sincronizar automáticamente el nuevo cliente de Odoo a la base local post-aprobación.
- Seguir el mismo patrón de capas, validaciones y optimistic locking que las cotizaciones.
- Integrar con la sincronización existente: cuando un lead se aprueba y se crea en Odoo, el cliente aparecerá para el vendedor externo asignado.

**Non-Goals:**
- No modificar el flujo de sincronización existente de clientes, productos o impuestos.
- No reemplazar la gestión de clientes en Odoo (Odoo sigue siendo fuente de verdad).
- No implementar edición de leads aprobados o sincronizados.
- No implementar flujo de rechazo con notificaciones push.
- No adjuntar archivos o documentos al lead (fuera de alcance inicial).

## Decisions

### D1: Modelo de datos unificado para Lead

Un lead representa un cliente potencial con estado. Se almacena localmente con UUID como PK, siguiendo el patrón de `QuotationDraft`.

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID PK | |
| company_name | VARCHAR(255) | Nombre de empresa (requerido) |
| contact_name | VARCHAR(255) | Nombre del contacto |
| email | VARCHAR(255) | Email del contacto |
| phone | VARCHAR(50) | Teléfono |
| mobile | VARCHAR(50) | Celular |
| street | VARCHAR(255) | Dirección |
| city | VARCHAR(100) | Ciudad |
| state | VARCHAR(100) | Provincia/Estado |
| zip | VARCHAR(20) | Código postal |
| country | VARCHAR(100) | País |
| vat | VARCHAR(50) | VAT/CUIT |
| notes | TEXT | Notas internas |
| status | VARCHAR(20) | `pendiente`, `aprobado`, `rechazado`, `sincronizado` |
| rejection_reason | TEXT | Motivo de rechazo (solo si status=rechazado) |
| created_by | UUID FK → users.id | Vendedor externo que creó el lead |
| reviewed_by | UUID FK → users.id | Admin que revisó el lead |
| reviewed_at | TIMESTAMP | Fecha de revisión |
| odoo_partner_id | INTEGER | ID del `res.partner` creado en Odoo (solo si sincronizado) |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |
| version | INTEGER DEFAULT 1 | Optimistic locking |

**Status flow:**
```
pendiente ──→ aprobado ──→ sincronizado
     │                        │
     └──→ rechazado           │
                              │
          (sincronizado se setea cuando Odoo responde OK)
```

### D2: Arquitectura de capas

Siguiendo el patrón de cotizaciones:

- **`api/leads.py`**: Router FastAPI con endpoints CRUD + approve/reject + sync.
- **`services/lead_service.py`**: Orquestación del flujo de negocio.
- **`repositories/lead_repository.py`**: Acceso a datos de la tabla `leads`.
- **`integrations/odoo/partner.py`**: Creación de `res.partner` en Odoo (nuevo módulo).
- **`services/lead_sync_service.py`**: Orquestación de la sincronización a Odoo (similar a `QuotationGenerationService`).

### D3: Endpoints API

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/leads` | Vendedor | Crear un lead (status=pendiente) |
| GET | `/leads` | Vendedor | Listar leads (propios; admin ve todos) |
| GET | `/leads/{id}` | Vendedor | Obtener detalle del lead |
| PUT | `/leads/{id}` | Vendedor | Actualizar lead (solo si pendiente, requiere version) |
| DELETE | `/leads/{id}` | Vendedor | Eliminar lead (solo si pendiente) |
| POST | `/leads/{id}/approve` | Admin | Aprobar lead |
| POST | `/leads/{id}/reject` | Admin | Rechazar lead (requiere rejection_reason) |

**Filtros en GET /leads:**
- `status`: filtrar por estado
- `q`: búsqueda por company_name, contact_name, email
- `date_from`, `date_to`: rango de fechas

### D4: Flujo de aprobación

1. Admin hace `POST /leads/{id}/approve`.
2. Backend valida: lead existe, status=pendiente, creado por usuario activo.
3. Backend asigna `reviewed_by = current_user`, `reviewed_at = now()`, `status = aprobado`.
4. **Inmediatamente después** se dispara la sincronización a Odoo (ver D5).
5. Si Odoo falla → el lead queda `aprobado` (no se revierte). Se puede reintentar la sincronización con un nuevo endpoint: `POST /leads/{id}/sync`.
6. Admin hace `POST /leads/{id}/reject` con `rejection_reason`.
7. Backend valida: lead existe, status=pendiente.
8. Backend setea `status = rechazado`, `rejection_reason`, `reviewed_by`, `reviewed_at`.

### D5: Integración con Odoo

Se crea `integrations/odoo/partner.py` con la función `create_partner()`:

```python
def create_partner(partner_data: dict) -> int:
    """
    Crea un res.partner en Odoo.
    partner_data: {
        'name': company_name,
        'company_name': company_name,
        'contact_name': contact_name,
        'email': email,
        'phone': phone,
        'mobile': mobile,
        'street': street,
        'city': city,
        'state_id': state_id,
        'zip': zip,
        'country_id': country_id,
        'vat': vat,
        'customer_rank': 1,  # Marcar como cliente
    }
    Retorna el odoo_id del partner creado.
    """
```

El vendedor externo que creó el lead se asigna al partner mediante `x_studio_vendedor_externo` (mismo campo usado en `sale.py`).

**Búsqueda de duplicados:** Antes de crear, se busca si ya existe un partner con el mismo VAT/CUIT o email. Si existe, se retorna error "El cliente ya existe en Odoo" y el lead se marca como `rechazado` con el motivo.

### D6: Sincronización post-creación

Después de crear el partner en Odoo, el lead se marca como `sincronizado` con el `odoo_partner_id`. El nuevo cliente será sincronizado a la base local en el próximo ciclo de `sync_customers()` (existente). No se implementa sincronización inmediata.

El flujo completo:
```
POST /leads/{id}/approve
  → status = aprobado
  → create_partner() en Odoo
  → status = sincronizado, odoo_partner_id = X
  → (el próximo sync_customers() traerá el cliente a la DB local)
```

### D7: Seguridad y autorización

- `get_current_user` protege todos los endpoints (JWT).
- Endpoints de approve/reject requieren `get_current_admin`.
- Endpoints de creación/edición son accesibles por cualquier usuario autenticado.
- En GET /leads, los vendedores externos solo ven sus propios leads (filtro por `created_by`). Los admins ven todos.
- En PUT/DELETE, se verifica que `created_by == current_user.id`.

### D8: Optimistic Locking

Mismo patrón que cotizaciones: campo `version` que se incrementa en cada actualización. El PUT requiere `version` en el body y retorna 409 si hay conflicto.

### D9: Manejo de errores

| Escenario | HTTP | Detalle |
|-----------|------|---------|
| Lead no encontrado | 404 | |
| Lead no editable (status != pendiente) | 409 | "Solo se puede modificar un lead en estado pendiente" |
| Lead ya aprobado/rechazado | 409 | "El lead ya fue revisado" |
| Conflicto de versión | 409 | "El lead fue modificado por otro usuario" |
| Cliente duplicado en Odoo | 409 | "El cliente ya existe en Odoo con el CUIT/email proporcionado" |
| Error de Odoo al crear partner | 502 | "Error al crear el cliente en Odoo. Intente nuevamente." |
| Vendedor externo no encontrado en Odoo | 400 | "El vendedor externo asignado no existe en Odoo" |
| Campos requeridos faltantes | 422 | Validación de schema |

### D10: Rechazo con motivo

El endpoint `POST /leads/{id}/reject` recibe:

```json
{
  "rejection_reason": "El cliente ya existe en nuestra base"
}
```

El motivo se almacena en el campo `rejection_reason` del lead.

## Risks / Trade-offs

- **[Dependencia de Odoo]**: Si Odoo no está disponible, la aprobación no puede completar la sincronización. **Mitigación**: El lead queda en `aprobado` y se puede reintentar la sincronización luego con `POST /leads/{id}/sync`.
- **[Duplicados]**: Un vendedor podría crear un lead para un cliente que ya existe en Odoo. **Mitigación**: Validación de duplicados por VAT/CUIT antes de crear en Odoo.
- **[Sincronización diferida]**: El cliente creado en Odoo no aparece inmediatamente en la app local. **Mitigación**: El ciclo de sync_customers() es manual/bajo demanda. Se podría agregar un trigger de sync inmediato post-creación como mejora futura.
- **[Datos incompletos]**: Los leads pueden crearse con datos mínimos (solo company_name). **Mitigación**: Solo `company_name` es requerido; el resto de campos son opcionales.

## Open Questions

- ¿Debemos sincronizar inmediatamente el partner creado a la DB local (además de marcarlo en el lead), o esperar el ciclo de sync? Decisión actual: esperar sync.
- ¿Notificar al vendedor externo cuando su lead sea aprobado/rechazado? Fuera de alcance por ahora.
- ¿Permitir que el vendedor externo edite un lead rechazado y re-enviarlo? Fuera de alcance por ahora.
