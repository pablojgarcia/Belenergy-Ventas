## ADDED Requirements

### Requirement: Botón "Nuevo cliente" en el selector de clientes
El sistema SHALL mostrar un botón "Nuevo cliente" en el modal de selección de clientes de "Nueva cotización", además de la lista de clientes existentes.

#### Scenario: Acceder al alta de cliente nuevo desde el modal
- **WHEN** el vendedor presiona "Nueva cotización" sin cliente preseleccionado y el modal de clientes se abre
- **THEN** el modal muestra la lista de clientes y un botón "Nuevo cliente" que al presionarse habilita el panel de cliente nuevo

#### Scenario: Selección de cliente existente
- **WHEN** el vendedor selecciona un cliente existente del modal
- **THEN** la cotización se asocia a ese cliente y el panel derecho muestra sus datos

### Requirement: Panel editable de cliente nuevo
El sistema SHALL mostrar en el panel derecho un formulario editable con los campos "Razón social" (obligatorio) y "CUIT" (opcional) cuando el vendedor elige crear un cliente nuevo.

#### Scenario: Completar razón social y CUIT
- **WHEN** el vendedor está en modo cliente nuevo e ingresa razón social y CUIT
- **THEN** el sistema valida el CUIT (formato) y muestra los datos ingresados en el panel

#### Scenario: Validación de razón social requerida
- **WHEN** el vendedor intenta guardar o generar sin ingresar la razón social en modo cliente nuevo
- **THEN** el sistema muestra un error indicando que la razón social es obligatoria

### Requirement: Cambio entre cliente existente y cliente nuevo
El sistema SHALL permitir al vendedor alternar entre un cliente existente y el modo cliente nuevo sin perder los productos agregados al borrador.

#### Scenario: Cambiar de cliente existente a cliente nuevo
- **WHEN** el vendedor tiene un cliente existente seleccionado y presiona "Nuevo cliente"
- **THEN** el panel cambia al formulario editable de cliente nuevo y los productos del borrador se mantienen

#### Scenario: Cambiar de cliente nuevo a cliente existente
- **WHEN** el vendedor está en modo cliente nuevo y presiona "Cambiar cliente"
- **THEN** se abre el modal de clientes existentes y, al elegir uno, el borrador se asocia a ese cliente
