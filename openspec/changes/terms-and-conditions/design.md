# Design: Términos y Condiciones en Cotizaciones

## Architecture

### Backend Model
```
terms_and_conditions
├── id (UUID PK)
├── name (String)
├── content (Text)
├── is_default (Boolean)
├── is_active (Boolean)
├── created_at (DateTime)
└── updated_at (DateTime)

quotation_drafts
└── terms_and_conditions_id (UUID FK → terms_and_conditions.id, nullable)
```

### API Routes
- `GET /terms-and-conditions` — list active T&C (public)
- `GET /terms-and-conditions/{id}` — get one (public)
- `POST /terms-and-conditions` — create (admin)
- `PUT /terms-and-conditions/{id}` — update (admin)
- `DELETE /terms-and-conditions/{id}` — soft delete (admin)

### Generation Flow
1. Draft has `terms_and_conditions_id` set
2. On generate, fetch T&C content from DB
3. Pass T&C content as `description` to `create_quotation()` → becomes `note` on `sale.order`
4. If no T&C selected, use `draft.notes` as before (backward compatible)

### Frontend
- T&C selector uses same pattern as customer picker (showDialog with searchable list)
- Preview dialog shows full T&C content before confirming selection
- Selected T&C shown as badge/chip in the card

## Key Decisions
- T&C replaces `notes` in the PDF (not concatenated) to avoid confusion
- Soft delete (`is_active`) instead of hard delete to preserve draft references
- Default T&C seeded in DB for immediate usability
- Admin-only CRUD; any authenticated user can view and select