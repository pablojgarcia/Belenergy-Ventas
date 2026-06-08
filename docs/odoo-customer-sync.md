# OpenSpec: odoo-customer-sync

## 1. Propuesta
Sincronizar los datos de clientes desde Odoo Online a la base de datos local de la aplicación. Esto asegura que los vendedores tengan acceso rápido y capaz de funcionar sin conexión a sus clientes asignados, y sienta las bases arquitectónicas para sincronizar presupuestos y órdenes de venta.

## 2. Especificación
- **Fuente de datos:** API de Odoo Online (XML-RPC o JSON-RPC).
- **Almacenamiento local:** Extender el esquema existente de SQLite/SQLAlchemy para incluir las entidades `Customer` y `Assignment`.
- **Mapeo de asignaciones:** Almacenar una relación entre `Vendedor` (Usuario) y `Cliente` (Socio).
- **Filtrado:** Implementar consultas a la base de datos para filtrar clientes por el ID del usuario actual.
- **Extensibilidad:** Utilizar una capa de abstracción para los trabajos de sincronización, permitiendo que futuros módulos (Presupuestos/Órdenes de Venta) se integren fácilmente.

## 3. Diseño
- **Entidades:**
    - `Customer`: id (ID de Odoo), nombre, email, teléfono, dirección, salesperson_id (FK).
- **API:**
    - Nuevo endpoint de backend: `/sync/customers` (Activado por Administrador/Sistema).
    - Endpoint actualizado: `GET /customers` (Soporta filtrado por `current_user`).
- **Flujo de datos:**
    1.  El trabajo de sincronización solicita datos de la API de Odoo.
    2.  La base de datos local realiza upserts de los registros de clientes.
    3.  Las tablas de relaciones se actualizan para reflejar el estado de asignación de Odoo.
    4.  El frontend de la aplicación solicita la lista filtrada al backend.

## 4. Tareas
- [ ] Definir el modelo `Customer` de SQLAlchemy y las relaciones en `Backend/app/models.py`.
- [ ] Crear las definiciones de `schemas.py` para la transferencia de datos de `Customer`.
- [ ] Implementar el módulo de servicio de API de Odoo en `Backend/app/odoo_service.py`.
- [ ] Crear el endpoint `/sync/customers` en `Backend/app/main.py`.
- [ ] Actualizar el endpoint de recuperación `/customers` para aplicar el filtrado por `salesperson_id`.
- [ ] Verificar la lógica de sincronización y filtrado con pruebas.
