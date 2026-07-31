# Tasks: Términos y Condiciones en Cotizaciones

## Backend
- [x] Add TermsAndConditions model to models.py
- [x] Add lightweight migration (terms_and_conditions table + terms_and_conditions_id column)
- [x] Create terms_and_conditions.py API routes (CRUD)
- [x] Add T&C schemas to schemas.py
- [x] Update DraftService to pass terms_and_conditions_id
- [x] Update QuotationGenerationService to use T&C content as sale.order note
- [x] Add seed data for default T&C in main.py
- [x] Register terms_and_conditions router in main.py
- [ ] Add backend tests for T&C feature

## Frontend
- [x] Create TermsAndConditions model (terms_and_conditions_model.dart)
- [x] Add getTermsAndConditions() to api_service.dart
- [x] Add T&C selector UI in create_quotation_page.dart
- [ ] Add T&C preview dialog

## OpenSpec
- [x] Create proposal.md
- [x] Create design.md
- [x] Create tasks.md
- [x] Create specs/

## Verification
- [ ] Run backend tests
- [ ] Run Flutter analyze
- [ ] Local commit