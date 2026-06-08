# Hoja de Ruta del Producto (Product Roadmap)

## Fase 0 - Fundamentos

Estado: En progreso

Objetivos:

* Autenticación
* Gestión de usuarios
* Infraestructura del proyecto
* Configuración de la base de datos
* Entorno Docker

Entregables:

* Registro de usuarios
* Inicio de sesión de usuarios
* Autenticación JWT

## Fase 1 - Modelo de Dominio de Clientes

Objetivos:

* Introducir la entidad cliente
* Introducir el modelo de propiedad del vendedor
* Extender roles de usuario

Entregables:

* Tabla de clientes
* Roles de usuario
* Relación cliente-vendedor

## Fase 2 - Sincronización de Clientes con Odoo

Objetivos:

* Recuperar clientes desde Odoo
* Recuperar asignaciones de clientes
* Sincronizar información de clientes

Entregables:

* Servicio de sincronización de clientes
* Proceso de sincronización programada
* Lógica de actualización de clientes

## Fase 3 - Portal de Clientes

Objetivos:

* Visibilidad de clientes para los vendedores

Entregables:

* Listado de clientes
* Búsqueda de clientes
* Vista de detalles de cliente

## Fase 4 - Información Comercial

Objetivos:

* Exponer la actividad comercial

Entregables:

* Sincronización de presupuestos
* Sincronización de órdenes de venta
* Historial comercial

## Fase 5 - Dashboard

Objetivos:

* Proporcionar KPIs de ventas

Entregables:

* Métricas de clientes
* Métricas de presupuestos
* Métricas de ventas
* Widgets para el dashboard

## Fase 6 - Funcionalidades Avanzadas

Objetivos:

* Mejorar la productividad

Posibles funcionalidades:

* Notificaciones
* Tareas
* Notas
* Línea de tiempo de actividad del cliente
* Optimizaciones para móviles
