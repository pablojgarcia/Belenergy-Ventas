## Context

El sistema actual tiene una base de datos PostgreSQL donde reside la tabla 'customers'. La aplicación requiere una nueva vista de usuario para listar clientes y sus respectivos vendedores.

## Goals / Non-Goals

**Goals:**
- Implementar la página 'my-customers'.
- Obtener datos de clientes y vendedores mediante una consulta SQL optimizada o un endpoint existente.

**Non-Goals:**
- No se realizarán cambios en el esquema de base de datos existente.
- No se implementarán funciones de edición o creación de clientes en esta primera fase.

## Decisions

- Se utilizará el stack tecnológico actual para la creación de la página y el endpoint de API necesario.
- La consulta SQL realizará un `JOIN` entre 'customers' y la tabla correspondiente de usuarios/vendedores (basado en 'salesperson_id').

## Risks / Trade-offs

- [Risk] Posible latencia al consultar un gran volumen de clientes. → Mitigación: Implementar paginación en el listado.
