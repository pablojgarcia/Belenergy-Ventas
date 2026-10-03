# Spec: Transparencia del caché en el motor de descuentos

## ADDED Requirements

### Requirement: El caché del motor de descuentos devuelve objetos equivalentes a los de la base

La capa de caché de `DiscountEngine` SHALL devolver objetos cuyos campos
declarados como UUID en el modelo (`DiscountRule.id`,
`DiscountRule.product_line_id`) tengan el mismo tipo y valor que los que
devuelve la consulta a la base de datos. El caché SHALL ser transparente: quien
consuma `_get_cached_rules` no SHALL poder distinguir el origen de las reglas a
partir de los tipos de sus campos.

#### Scenario: Las reglas servidas desde caché referencian la misma ProductLine que las de la base

- **WHEN** se invocan `_get_cached_rules(seller_type, [product_line_id])` con el caché caliente
- **THEN** cada regla devuelta SHALL tener `rule.product_line_id` igual a `product_line_id`
- **AND** el tipo de `rule.product_line_id` SHALL ser `uuid.UUID`, el mismo tipo que devuelve la columna `Uuid` del modelo

#### Scenario: Un lote de reglas cacheadas se indexa bajo la misma clave que uno leído de la base

- **WHEN** se arma `rules_by_line` a partir de reglas obtenidas del caché
- **AND** se busca con `rules_by_line.get(product_line.id, [])` donde `product_line.id` proviene de `ProductLine.id`
- **THEN** el lookup SHALL encontrar las reglas de esa línea de producto
- **AND** no SHALL devolver una lista vacía

### Requirement: El resultado de una evaluación no depende del estado del caché

`DiscountEngine.evaluate_lines` SHALL devolver el mismo resultado para las
mismas entradas, independientemente de si las reglas se resuelven desde el caché
o desde la base de datos. La única condición bajo la cual puede diferir es un
cambio real en los datos de `discount_rules`.

#### Scenario: Dos evaluaciones consecutivas con caché inactivo dan el mismo resultado

- **WHEN** se evalúa una línea de producto dos veces consecutivas con el caché inactivo
- **THEN** ambas respuestas SHALL ser idénticas, incluyendo `max_discount`, `tier`, `exceeded` y `message`

#### Scenario: La segunda evaluación lee las reglas desde el caché y no altera el resultado

- **WHEN** se evalúa una línea de producto con el caché inactivo (la llamada resuelve desde la base y puebla el caché)
- **AND** se vuelve a evaluar la misma línea dentro de la ventana de TTL (la llamada resuelve desde el caché)
- **THEN** la segunda respuesta SHALL ser idéntica a la primera
- **AND** `max_discount` SHALL ser el valor del tramo aplicable, no `None`

#### Scenario: Una línea sin regla aplicable no se confunde con una línea cuyas reglas no se encontraron

- **WHEN** no existe ninguna regla que matchee la condición para la línea de producto
- **THEN** la respuesta SHALL informar que no hay regla aplicable
- **AND** ese resultado SHALL ser el mismo con caché frío y con caché caliente

### Requirement: La suite de tests puede reproducir el fallo del caché

La suite de tests SHALL poder ejecutar la rama del caché de
`DiscountEngine._get_cached_rules`. Un test que ejercite `evaluate_lines` sin
levantar un Redis falso SHALL considerarse insuficiente como cobertura de este
comportamiento, porque en ese caso la rama del caché no se ejecuta.

#### Scenario: El test falsifica Redis en lugar de omitir el caché

- **WHEN** se corre la suite de tests
- **THEN** el test de regresión del caché SHALL inyectar un cliente Redis falso
- **AND** las reglas SHALL pasar por la serialización real de `cache_service` (`json.dumps` / `json.loads`)

#### Scenario: El fallo se detecta contra el código sin el fix

- **WHEN** el test de regresión se corre contra el motor sin la corrección
- **THEN** SHALL fallar