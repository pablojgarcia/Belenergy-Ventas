## ADDED Requirements

### Requirement: Listar cotizaciones del vendedor
El sistema DEBE listar las cotizaciones creadas por el vendedor autenticado.

#### Scenario: Listado exitoso
- **WHEN** el vendedor autenticado solicita el listado de cotizaciones
- **THEN** el sistema devuelve todas las cotizaciones donde `user_id` coincide con el usuario autenticado

#### Scenario: Sin cotizaciones
- **WHEN** el vendedor no tiene cotizaciones creadas
- **THEN** el sistema devuelve una lista vacía

### Requirement: Filtros en listado
El sistema DEBE permitir filtrar cotizaciones por estado (draft, sent, sale, cancel).

#### Scenario: Filtrar por estado
- **WHEN** el vendedor especifica un estado en la consulta
- **THEN** el sistema devuelve solo las cotizaciones con ese estado
