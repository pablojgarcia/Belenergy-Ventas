# Proposal: Términos y Condiciones en Cotizaciones

## Summary
Add a configurable set of Terms and Conditions (T&C) that can be selected when generating a quotation. The selected T&C content is included as the `note` on the Odoo `sale.order`, appearing on the generated PDF.

## Problem
Currently, quotations have a free-form `notes` field that maps to Odoo's `sale.order.note`. There is no way to use predefined T&C sets or standardize the terms across quotations.

## Solution
1. A `terms_and_conditions` table with preloaded T&C sets
2. A `terms_and_conditions_id` foreign key on `quotation_drafts`
3. When generating, the selected T&C content replaces `draft.notes` as the `note` on the Odoo sale order
4. Admin CRUD API for managing T&C sets
5. Frontend selector in the create quotation page

## Non-goals
- ARCA/CUIT validation integration (separate feature)
- T&C versioning or approval workflow
- Per-customer T&C overrides

## Open questions
- Should T&C content be combined with draft notes or replace them entirely? → T&C replaces notes in the PDF; notes remain as internal data.
- Should there be a default T&C set? → Yes, one default set is seeded.