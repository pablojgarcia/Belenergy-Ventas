## ADDED Requirements

### Requirement: List customers and salesperson
The system SHALL provide a page 'my-customers' that lists all customers from the database, displaying the customer's name and the associated salesperson's name and email.

#### Scenario: Successful data display
- **WHEN** user navigates to '/my-customers'
- **THEN** system displays a table with customer name and salesperson contact info

#### Scenario: No customers found
- **WHEN** user navigates to '/my-customers' and there are no customers
- **THEN** system displays an empty state message
