## ADDED Requirements

### Requirement: Ver detalle de cotización
El sistema DEBE mostrar el detalle completo de una cotización individual, incluyendo líneas de producto.

#### Scenario: Detalle exitoso
- **WHEN** el vendedor solicita el detalle de una cotización por su ID
- **THEN** el sistema devuelve la información local más las líneas de producto desde Odoo

#### Scenario: Cotización no encontrada
- **WHEN** el vendedor solicita una cotización que no existe
- **THEN** el sistema responde con error 404

#### Scenario: Cotización de otro vendedor
- **WHEN** el vendedor solicita una cotización creada por otro usuario
- **THEN** el sistema responde con error 403
