## 1. Backend: eliminar Leads

- [x] 1.1 Eliminar `Backend/app/api/leads.py` y su router en `main.py`
- [x] 1.2 Eliminar `Backend/app/services/lead_service.py` y `Backend/app/repositories/lead_repository.py`
- [x] 1.3 Eliminar `Backend/app/integrations/odoo/crm_lead.py` y mover `check_cuit_exists` → `check_vat_exists` en `partner.py`
- [x] 1.4 Eliminar el modelo `Lead` de `models.py`, la creación de la tabla en `main.py` y los schemas de lead en `schemas.py`
- [x] 1.5 Crear migración Alembic para `drop table leads`
- [x] 1.6 Verificar que no queden imports rotos (tests + app importan OK)

## 2. Backend: cliente nuevo en la cotización

- [x] 2.1 Agregar columnas `new_client_name` y `new_client_vat` a `quotation_drafts` (modelo + migración + fallback en `main.py`)
- [x] 2.2 Crear `Backend/app/utils/cuit.py` con `validar_cuit(cuit)` (11 dígitos + mod-11 AFIP)
- [x] 2.3 Crear `Backend/app/services/customer_creation_service.py` (validar CUIT + chequeo duplicados local/Odoo + `odoo_create_partner` + `upsert` local)
- [x] 2.4 Actualizar schemas de draft (`QuotationDraftCreate`, `QuotationDraftUpdate`, `QuotationDraftOut`) con `new_client_name` / `new_client_vat`
- [x] 2.5 Actualizar `DraftService.create/update/_enrich` para persistir y exponer `new_client_*`
- [x] 2.6 Modificar `QuotationGenerationService.generate` para crear el cliente cuando `customer_id` es nulo y `new_client_name` está presente

## 3. Frontend: cliente nuevo en la cotización

- [x] 3.1 Agregar botón "Nuevo cliente" al modal `_CustomerPickerDialog` en `create_quotation_page.dart`
- [x] 3.2 Implementar modo cliente nuevo: panel derecho editable con Razón social + CUIT y validación
- [x] 3.3 Actualizar `_buildPayload`, `_loadDraft`, `_loadCustomer` y validaciones para `new_client_*` sin `customer_id`

## 4. Frontend: eliminar Leads

- [x] 4.1 Eliminar pantallas `leads_page.dart`, `create_lead_page.dart`, `lead_detail_page.dart`, `lead_approval_page.dart`
- [x] 4.2 Eliminar rutas de leads en `config/router.dart`
- [x] 4.3 Eliminar destino Leads del `NavigationRail` y `NavigationBar` en `responsive_shell.dart` (reindexar tabs)
- [x] 4.4 Eliminar de `home_page.dart`: quick item Leads, tarjeta de stats Leads, llamada a `getLeads`, botón admin "Aprobar leads"
- [x] 4.5 Eliminar métodos de leads en `services/api_service.dart`
- [x] 4.6 `flutter analyze` sin errores

## 5. Docs y OpenSpec

- [x] 5.1 Actualizar `MANUAL.md` (eliminar sección Leads, renumerar, documentar cliente nuevo + validación CUIT)
- [ ] 5.2 Actualizar `docs/current-state.md`, `docs/roadmap.md`, `docs/vision.md`, `docs/architecture.md`
- [x] 5.3 Archivar `openspec/changes/lead-management` y verificar READMEs por referencias a leads

## 6. Pruebas locales

- [x] 6.1 Tests unitarios de `validar_cuit` (válidos, inválidos, prefijos 20/23/24/27)
- [x] 6.2 Tests de `generate` con cliente nuevo (mock Odoo) y rechazo por duplicado
- [x] 6.3 `pytest` completo del backend
- [x] 6.4 E2E local contra Odoo real: borrador con cliente nuevo → generar → verificar partner + sale.order (y limpiar)

## 7. Push y deploy

- [ ] 7.1 Commit y push del branch
- [ ] 7.2 Crear PR, esperar CI/CD y merge
- [ ] 7.3 Verificar deploy (backend Railway + frontend Cloudflare) y smoke test en producción
