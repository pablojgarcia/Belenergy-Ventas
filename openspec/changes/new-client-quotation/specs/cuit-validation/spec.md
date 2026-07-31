## ADDED Requirements

### Requirement: Validación de formato y dígito verificador del CUIT
El sistema SHALL validar el CUIT como exactamente 11 dígitos con dígito verificador calculado por el algoritmo mod-11 de AFIP, tanto en el frontend (feedback inmediato) como en el backend (autoritativo).

#### Scenario: CUIT válido
- **WHEN** se ingresa un CUIT con 11 dígitos y dígito verificador correcto
- **THEN** el sistema lo acepta como válido y continúa el flujo

#### Scenario: CUIT con formato incorrecto
- **WHEN** se ingresa un CUIT con menos de 11 dígitos, con letras o con dígito verificador incorrecto
- **THEN** el sistema lo rechaza con un mensaje claro indicando que el CUIT es inválido

#### Scenario: CUIT vacío
- **WHEN** el vendedor no ingresa CUIT (deja el campo vacío)
- **THEN** el sistema permite continuar ya que el CUIT es opcional

### Requirement: Prevención de duplicados de cliente por CUIT
El sistema SHALL rechazar la creación de un cliente nuevo cuando el CUIT ingresado ya exista en la base local de clientes o en Odoo, devolviendo un error claro.

#### Scenario: CUIT ya existente en la base local
- **WHEN** se genera una cotización con un CUIT que ya existe en la tabla local `customers`
- **THEN** el sistema devuelve un error 409 indicando que ya existe un cliente con ese CUIT

#### Scenario: CUIT ya existente en Odoo
- **WHEN** se genera una cotización con un CUIT que ya existe como `res.partner` en Odoo pero aún no se sincronizó a la base local
- **THEN** el sistema devuelve un error 409 indicando que ya existe un cliente con ese CUIT

#### Scenario: Sin CUIT, sin chequeo de duplicados
- **WHEN** se genera una cotización de cliente nuevo sin CUIT
- **THEN** el sistema no realiza chequeo de duplicados y crea el cliente con la razón social provista
