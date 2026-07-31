## 1. Modelo de datos y migración

- [x] 1.1 Agregar modelo `Lead` en `models.py` con campos: id (UUID), company_name, contact_name, email, phone, mobile, street, city, state, zip, country, vat, notes, status, rejection_reason, created_by (FK→users), reviewed_by (FK→users), reviewed_at, odoo_partner_id, version, created_at, updated_at
- [x] 1.2 Agregar schemas Pydantic en `schemas.py`: `LeadCreate`, `LeadUpdate`, `LeadOut`, `LeadApprove`, `LeadReject`
- [x] 1.3 Crear migración Alembic para la tabla `leads` (auto-create via Base.metadata.create_all en main.py)

## 2. Integración con Odoo

- [x] 2.1 Crear `integrations/odoo/partner.py` con función `create_partner()` que crea `res.partner` en Odoo
- [x] 2.2 Implementar búsqueda de duplicados en `create_partner()` por VAT/CUIT y email antes de crear
- [x] 2.3 Asignar `x_studio_vendedor_externo` al partner creado según el creador del lead
- [x] 2.4 Retornar el `odoo_id` del partner creado

## 3. Repositorio

- [x] 3.1 Crear `repositories/lead_repository.py` con métodos: `create`, `get_by_id`, `get_by_user` (filtrado por creador), `get_all` (para admins), `update`, `delete`
- [x] 3.2 Implementar filtros en `get_by_user`/`get_all`: status, q (búsqueda), date_from, date_to

## 4. Servicio de negocio

- [x] 4.1 Crear `services/lead_service.py` con métodos CRUD y validaciones (RN-001 a RN-005)
- [x] 4.2 Implementar `approve_lead()`: validar estado, setear approved_by/reviewed_at, cambiar status, disparar sync a Odoo
- [x] 4.3 Implementar `reject_lead()`: validar estado, guardar rejection_reason, cambiar status
- [x] 4.4 Implementar `sync_lead_to_odoo()`: llamar a `create_partner()`, capturar odoo_id, marcar status=sincronizado
- [x] 4.5 Implementar optimistic locking en actualizaciones (version check)

## 5. API endpoints

- [x] 5.1 Crear `api/leads.py` con router y endpoints: POST /leads, GET /leads, GET /leads/{id}, PUT /leads/{id}, DELETE /leads/{id}
- [x] 5.2 Implementar endpoints de admin: POST /leads/{id}/approve, POST /leads/{id}/reject, POST /leads/{id}/sync
- [x] 5.3 Proteger endpoints de admin con `get_current_admin`
- [x] 5.4 Filtrar leads por created_by para vendedores externos; mostrar todos para admins
- [x] 5.5 Registrar router en `main.py`

## 6. Frontend Flutter - Modelo y API

- [x] 6.1 Crear modelo `Lead` en `Ventas/lib/models/lead_model.dart`
- [x] 6.2 Agregar métodos HTTP en `api_service.dart`: getLeads, getLead, createLead, updateLead, deleteLead, approveLead, rejectLead

## 7. Frontend Flutter - Pantallas de lead

- [x] 7.1 Crear `leads_page.dart`: lista de leads con filtros por estado y búsqueda
- [x] 7.2 Crear `create_lead_page.dart`: formulario para crear/editar lead
- [x] 7.3 Crear `lead_detail_page.dart`: detalle del lead con acciones (editar/eliminar si pendiente)
- [x] 7.4 Agregar navegación desde home_page.dart a leads_page.dart

## 8. Frontend Flutter - Panel de aprobación

- [x] 8.1 Crear `lead_approval_page.dart` (solo visible para admins): lista de leads pendientes
- [x] 8.2 Implementar acciones de aprobar/rechazar con diálogo de confirmación y motivo de rechazo
- [x] 8.3 Agregar navegación al panel de aprobación desde home_page.dart (solo admin) - ruta `/leads/approval` registrada en router

## 9. Pruebas y validación (manuales, requieren entorno con Odoo)

- [ ] 9.1 Probar flujo completo: crear lead → listar → editar → aprobar → verificar sincronización
- [ ] 9.2 Probar flujo de rechazo con motivo
- [ ] 9.3 Probar validaciones: lead inexistente (404), lead ya revisado (409), optimistic locking (409), duplicado en Odoo (409)
- [ ] 9.4 Probar autorización: vendedor no puede ver leads de otro, admin puede ver todos
