# OpenSpec: odoo-customer-sync

## 1. Proposal
Synchronize customer data from Odoo Online into the local application database. This ensures salespeople have quick, offline-capable access to their assigned customers and lays the architectural foundation for syncing quotations and sales orders.

## 2. Specification
- **Data Source:** Odoo Online API (XML-RPC or JSON-RPC).
- **Local Storage:** Extend the existing SQLite/SQLAlchemy schema to include `Customer` and `Assignment` entities.
- **Assignment Mapping:** Store a relationship mapping between `Salesperson` (User) and `Customer` (Partner).
- **Filtering:** Implement database queries to filter customers by the current user's ID.
- **Extensibility:** Use an abstraction layer for sync jobs to allow future modules (Quotations/Sales Orders) to integrate easily.

## 3. Design
- **Entities:**
    - `Customer`: id (Odoo ID), name, email, phone, address, salesperson_id (FK).
- **API:**
    - New backend endpoint: `/sync/customers` (Triggered by Admin/System).
    - Updated endpoint: `GET /customers` (Supports filter by `current_user`).
- **Data Flow:**
    1.  Sync job requests data from Odoo API.
    2.  Local DB upserts customer records.
    3.  Relationship tables updated to reflect Odoo assignment state.
    4.  Application frontend requests filtered list from backend.

## 4. Tasks
- [ ] Define SQLAlchemy `Customer` model and relationships in `Backend/app/models.py`.
- [ ] Create `schemas.py` definitions for `Customer` data transfer.
- [ ] Implement Odoo API service module in `Backend/app/odoo_service.py`.
- [ ] Create `/sync/customers` endpoint in `Backend/app/main.py`.
- [ ] Update `/customers` retrieval endpoint to enforce `salesperson_id` filtering.
- [ ] Verify synchronization and filtering logic with tests.
