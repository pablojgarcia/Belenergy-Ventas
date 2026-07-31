## ADDED Requirements

### Requirement: Alta de cliente nuevo al generar la cotización
El sistema SHALL permitir crear un cliente nuevo en Odoo y sincronizarlo a la base local como parte de la generación de una cotización, cuando el borrador tenga `customer_id` nulo y `new_client_name` poblado.

#### Scenario: Generar cotización de cliente nuevo
- **WHEN** el vendedor presiona "Generar cotización" en un borrador con `new_client_name` y sin `customer_id`
- **THEN** el sistema crea el `res.partner` en Odoo con `vendedor_externo` igual al email del usuario, sincroniza el cliente a la base local, asigna el `customer_id` al borrador y crea la `sale.order`

#### Scenario: Borrador sin cliente y sin nombre de cliente nuevo
- **WHEN** se intenta generar una cotización sin `customer_id` y sin `new_client_name`
- **THEN** el sistema rechaza la generación con un error 400 indicando que el borrador debe tener un cliente asignado

#### Scenario: Error en Odoo al crear el partner
- **WHEN** Odoo falla al crear el `res.partner`
- **THEN** el sistema marca el borrador como fallido y devuelve un error 502 con el detalle

### Requirement: Persistencia de los datos del cliente nuevo en el borrador
El sistema SHALL persistir `new_client_name` y `new_client_vat` (ambos opcionales) en el borrador, permitiendo guardarlo y editarlo antes de generar.

#### Scenario: Guardar borrador con cliente nuevo
- **WHEN** el vendedor guarda un borrador con `new_client_name` y `new_client_vat` y sin `customer_id`
- **THEN** el sistema lo persiste con esos valores y lo devuelve en el detalle del borrador

#### Scenario: Editar datos del cliente nuevo
- **WHEN** el vendedor modifica `new_client_name` o `new_client_vat` de un borrador en estado borrador
- **THEN** el sistema actualiza esos valores manteniendo el versionado del borrador

### Requirement: Asignación de vendedor externo en el cliente creado
El sistema SHALL asignar como `vendedor_externo` (campo `x_studio_vendedor_externo`) el partner de Odoo del usuario autenticado que genera la cotización, al crear el cliente nuevo.

#### Scenario: Cliente nuevo con vendedor externo
- **WHEN** un vendedor crea un cliente nuevo al generar una cotización
- **THEN** el `res.partner` creado en Odoo queda asignado al vendedor externo del usuario en el campo `x_studio_vendedor_externo`

#### Scenario: Usuario sin partner en Odoo
- **WHEN** el usuario autenticado no tiene un partner de Odoo identificable por email
- **THEN** el sistema crea el cliente sin vendedor externo asignado y no falla la operación
