# Spec: TermsAndConditions Model

## Model Fields
- `id`: UUID, primary key
- `name`: String, required, display name of the T&C set
- `content`: Text, required, the full T&C text
- `is_default`: Boolean, default False
- `is_active`: Boolean, default True (soft delete)
- `created_at`: DateTime, server default
- `updated_at`: DateTime, on update

## Relationships
- `QuotationDraft.terms_and_conditions_id` → `TermsAndConditions.id` (nullable FK)

## Constraints
- Active records only returned by list endpoint
- Soft delete preserves draft references