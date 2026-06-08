# Design: Customer Domain Model

## Entity Model Design

### 1. User (Extension)
Extend the existing `User` entity to support role-based access control.
- **New Field:** `role` (String: 'admin', 'salesperson')

### 2. Customer
Introduce the `Customer` entity to manage client information locally.
- **Fields:**
    - `id`: Internal Primary Key (Integer).
    - `odoo_id`: External reference to Odoo (Integer, Indexed, Unique).
    - `name`: Full name or company name (String).
    - `email`: Customer email (String, Indexed).
    - `phone`: Contact number (String).
    - `address`: Physical location (String).
    - `salesperson_id`: Foreign Key referencing `User.id` (Nullable for unassigned customers).
    - `created_at` / `updated_at`: Timestamp tracking.

## Relationships
- **One-to-Many:** `User` (Salesperson) -> `Customer` (Clients). One salesperson can manage multiple customers; each customer can have one assigned salesperson.

## Future-Proofing
- The schema uses an `odoo_id` field to prevent data duplication during future synchronization cycles and to allow for simple lookups during API calls.
- The `role` field in `User` allows for easy expansion of administrative vs. user-level logic.
