# Arquitectura

## Visión General

El portal de ventas de Belenergy es una aplicación web/móvil diseñada para representantes de ventas.

El sistema se integra con Odoo Online, que actúa como fuente de datos principal para clientes, presupuestos y órdenes de venta.

La aplicación consiste en:

* Frontend en Flutter
* Backend en FastAPI
* Base de datos PostgreSQL
* Integración con Odoo Online

## Arquitectura de Alto Nivel

```text
Odoo Online
     │
     │ API
     ▼
Backend en FastAPI
     │
     │ API REST
     ▼
Aplicación Flutter
```

## Backend

Stack tecnológico:

* FastAPI
* SQLAlchemy
* PostgreSQL
* Autenticación JWT

Responsabilidades:

* Autenticación de usuarios
* Autorización
* Gestión de clientes
* Sincronización con Odoo
* Aplicación de reglas de negocio

## Frontend

Stack tecnológico:

* Flutter
* Provider
* Dio

Responsabilidades:

* Autenticación de usuarios
* Listado de clientes
* Detalles de cliente
* Panel de control (Dashboard)
* Visualización de presupuestos y órdenes de venta

## Base de Datos

Entidades actuales:

### Usuario (User)

Campos:

* id
* email
* username
* hashed_password
* is_active
* created_at

Entidades futuras:

### Cliente (Customer)

* id
* odoo_id
* name
* email
* phone
* salesperson_id

## Integración con Odoo

Odoo Online es la fuente de la verdad.

La siguiente información será sincronizada desde Odoo:

* Clientes
* Asignaciones de vendedores
* Presupuestos
* Órdenes de venta

Las asignaciones de clientes se mantienen en Odoo y no pueden ser modificadas desde el Portal de Ventas.

## Seguridad

Autenticación:

* Tokens JWT

Autorización:

* Los vendedores solo pueden acceder a clientes asignados
* Los administradores pueden acceder a toda la información

## Despliegue

Entorno actual:

* Docker
* Docker Compose

Entornos futuros:

* Desarrollo
* Staging
* Producción
