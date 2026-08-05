# Tareas: Motor de Reglas de Descuento

## 1. Modelo de datos
- [x] `ProductLine` table (key, name, is_active)
- [x] `DiscountRule` table (seller_type, product_line_id, condition_type, min/max, max_discount, requires_approval, is_active)
- [x] `User.seller_type` column
- [x] `Product.product_line_id` column
- [x] Snapshot fields in `QuotationDraftLine`

## 2. Seed
- [x] `seed_discount_rules.py` con matriz del Excel
- [x] `seed_product_lines()` y `seed_discount_rules()` en `main.py`

## 3. Sync
- [x] Ancestor-walk en `sync.py` para resolver `product_line_id`

## 4. Motor
- [x] `discount_engine.py` con `evaluate(draft, user)`
- [x] Bandas amount y qty genéricas
- [x] requires_approval y message por línea

## 5. Enforcement
- [x] Validación en `QuotationGenerationService.generate()`
- [x] Snapshot por línea al generar
- [x] 409 con detalle por línea

## 6. API
- [x] `api/discount_rules.py` CRUD admin
- [x] `GET /quotation-drafts/{id}/discount-rules` (read)
- [x] `seller_type` en schemas de User

## 7. Migraciones
- [x] Migraciones ligeras en `main.py`

## 8. Tests
- [x] `test_discount_rules.py` (17 tests)

## 9. OpenSpec
- [x] proposal.md, design.md, specs/, tasks.md

## 10. .env.local
- [x] Odoo de prueba configurado (gitignored)
