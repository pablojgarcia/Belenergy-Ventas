# Manual de Usuario — Belenergy Ventas

Sistema de gestión de ventas, cotizaciones y leads integrado con **Odoo v19**.

---

## Índice

1. [Introducción](#1-introducción)
2. [Acceso y Autenticación](#2-acceso-y-autenticación)
3. [Dashboard / Inicio](#3-dashboard--inicio)
4. [Clientes](#4-clientes)
5. [Productos](#5-productos)
6. [Cotizaciones](#6-cotizaciones)
7. [Leads](#7-leads)
8. [Administración](#8-administración)
9. [Solución de Problemas](#9-solución-de-problemas)

---

## 1. Introducción

**Belenergy Ventas** es una aplicación web para la gestión de clientes, cotizaciones y leads, sincronizada en tiempo real con Odoo v19.

**URL de acceso:** [https://ventas.belenergy-arg.workers.dev](https://ventas.belenergy-arg.workers.dev)

### Requisitos

- Navegador web moderno (Chrome, Firefox, Edge, Safari).
- Conexión a Internet.
- Credenciales de usuario provistas por el administrador.

---

## 2. Acceso y Autenticación

### 2.1. Iniciar sesión

1. Ingrese a la URL del sistema.
2. En la pantalla de login, complete:
   - **Correo electrónico:** su email registrado.
   - **Contraseña:** su contraseña.
3. Presione **Ingresar**.

Si las credenciales son correctas, accederá al dashboard principal. Si no, verá un mensaje de error.

### 2.2. Cerrar sesión

1. Toque su avatar (iniciales) en la barra superior.
2. Seleccione **Cerrar sesión**.
3. Confirme en el diálogo.

> La sesión se mantiene activa incluso al cerrar el navegador. Para seguridad, cierre sesión en dispositivos compartidos.

---

## 3. Dashboard / Inicio

Al iniciar sesión, se muestra el panel principal con tarjetas de resumen:

| Tarjeta | Descripción |
|---|---|
| **Clientes** | Cantidad total de clientes sincronizados |
| **Presupuestos** | Cantidad de borradores y cotizaciones generadas |
| **Productos** | Cantidad de productos activos |
| **Leads** | Cantidad de leads registrados |

Desde aquí puede acceder rápidamente a cada sección tocando su tarjeta.

### 3.1. Perfil de usuario

Toque su avatar (iniciales) en la barra superior para abrir el panel de perfil. Muestra:

- Nombre y email del usuario
- Rol (admin / vendedor)

**Usuarios administradores** ven opciones adicionales:

| Botón | Acción |
|---|---|
| **Sincronizar clientes** | Trae todos los clientes desde Odoo |
| **Sincronizar productos** | Trae productos e impuestos desde Odoo |
| **Aprobar leads** | Abre la pantalla de aprobación de leads |

---

## 4. Clientes

### 4.1. Listado de clientes

Acceda desde el menú lateral o la tarjeta del dashboard.

- **Vista escritorio:** tabla con columnas Nombre, CUIT, Email, Teléfono, Dirección, Acciones.
- **Vista móvil:** tarjetas individuales con la misma información.

### 4.2. Buscar clientes

Escriba en el campo de búsqueda para filtrar por:

- Nombre, Email, Teléfono, CUIT, Vendedor interno, Compañía, Dirección.

### 4.3. Ver contacto

Toque el ícono 👁️ (o **Ver contacto**) para abrir el diálogo de detalle. Muestra:

- Información completa del cliente
- Botones para copiar email, teléfono y dirección al portapapeles
- Lista de **contactos asociados** (nombre, email, teléfono)

### 4.4. Crear cotización desde cliente

Toque el ícono 📄 **Nueva cotización** para crear una cotización con ese cliente preseleccionado.

---

## 5. Productos

### 5.1. Listado de productos

Acceda desde el menú lateral o la tarjeta del dashboard.

- **Vista escritorio:** tabla con columnas Imagen, Título, Código, Precio, Categoría, IVA.
- **Vista móvil:** tarjetas con imagen, nombre, código y precio.

### 5.2. Buscar productos

Filtre por nombre, código o categoría.

### 5.3. Precios

Los precios se sincronizan desde la lista de precios USD de Odoo. Si un producto no tiene precio USD configurado, se muestra su precio de venta estándar.

---

## 6. Cotizaciones

### 6.1. Listado de cotizaciones

Acceda desde el menú lateral. Muestra todos los borradores y cotizaciones generadas, ordenados por fecha de creación (más recientes primero).

**Filtros disponibles:**

| Filtro | Muestra |
|---|---|
| Todos | Todos los borradores y cotizaciones |
| Borrador | Solo cotizaciones en edición |
| Generadas | Solo cotizaciones enviadas a Odoo |

**Estados:**

| Estado | Color | Significado |
|---|---|---|
| Borrador | 🟠 Naranja | En edición, sin enviar |
| Generada | 🟢 Verde | Enviada a Odoo |
| Error | 🔴 Rojo | Falló al generar |

### 6.2. Crear una cotización

1. Presione **Nueva cotización** en la barra superior.
2. **Seleccionar cliente:**
   - Si viene desde la pantalla de cliente, ya estará preseleccionado.
   - Si no, se abrirá un buscador de clientes. Escriba para filtrar y seleccione uno.
   - Puede presionar **Cambiar cliente** para elegir otro.
3. **Agregar productos:**
   - Presione **Agregar producto**.
   - Busque por nombre, código o código de barras.
   - Seleccione el producto; se agrega a la tabla con cantidad 1.
   - Ajuste la cantidad con los botones ➕/➖.
   - Puede eliminar un renglón con el botón **✕**.
4. **Notas:** (opcional) agregue una descripción interna.
5. **Guardar:** presione **Guardar** para guardar el borrador.
6. **Generar:** presione **Generar cotización** para crear la orden de venta en Odoo.

### 6.3. Editar una cotización (borrador)

1. Desde el listado, toque **Ver detalle** en una cotización en estado **Borrador**.
2. Presione **Editar**.
3. Modifique productos, cantidades o notas.
4. Presione **Guardar** o **Generar cotización**.

### 6.4. Ver detalle de cotización

Muestra la información completa:

- Cliente, estado, fecha, notas
- Tabla de productos con cantidades, precios, IVA y totales
- Totales: Subtotal, IVA, Total general

**Acciones disponibles:**

| Estado | Acciones |
|---|---|
| Borrador | Editar, Generar |
| Generada | Descargar PDF |

### 6.5. Descargar PDF

En cotizaciones ya generadas, presione el botón **Descargar PDF**. El archivo se guarda en su dispositivo.

---

## 7. Leads

Un **lead** es un potencial cliente que aún no está registrado en el sistema. El flujo completo es:

```
Crear lead → Enviar a Odoo → Aprobar (admin) → Crear cliente → Crear cotización
```

### 7.1. Listado de leads

Acceda desde el menú lateral.

**Filtros disponibles:**

| Filtro | Muestra |
|---|---|
| Todos | Todos los leads |
| Pendiente | Leads pendientes de revisión |
| Aprobado | Leads aprobados |
| Rechazado | Leads rechazados |
| Sincronizado | Leads ya enviados a Odoo |

**Estados:**

| Estado | Color | Significado |
|---|---|---|
| Pendiente | 🟠 Naranja | Creado, esperando revisión |
| Aprobado | 🟢 Verde | Aprobado por admin |
| Rechazado | 🔴 Rojo | Rechazado por admin |
| Sincronizado | 🔵 Azul | Enviado a Odoo CRM |

### 7.2. Crear un lead

1. Presione **Nuevo lead**.
2. Complete los campos obligatorios (*):
   - **Nombre de la empresa** (obligatorio)
   - **CUIT** (obligatorio)
   - Datos de contacto (email, teléfono, celular) — opcional
   - Dirección (calle, ciudad, provincia, CP, país) — opcional
   - **Notas** — opcional
3. Presione **Crear lead**.

El lead queda en estado **Pendiente**.

### 7.3. Editar un lead

Solo se pueden editar leads en estado **Pendiente**.

1. Desde el listado, toque el lead para ver su detalle.
2. Presione el ícono ✏️ **Editar**.
3. Modifique los campos necesarios.
4. Presione **Guardar cambios**.

### 7.4. Enviar lead a Odoo CRM

Puede enviar un lead a Odoo desde:

- **Listado:** presione el botón **Enviar** en el lead (visible para Pendiente y Aprobado).
- **Detalle:** la sincronización se dispara automáticamente al aprobar.

Al enviar, el sistema:

1. Verifica que el CUIT no exista ya en Odoo.
2. Crea la oportunidad en Odoo CRM.
3. Asigna el **vendedor externo** (usuario que creó el lead).
4. Asigna el **vendedor interno** (configurado por admin en el usuario).

### 7.5. Aprobar / Rechazar leads (Admin)

Acceda desde **Perfil de usuario → Aprobar leads**.

1. Se muestran todos los leads **Pendientes**.
2. Para cada lead:
   - Presione ✅ **Aprobar** — el lead se sincroniza automáticamente a Odoo CRM.
   - Presione ❌ **Rechazar** — ingrese el motivo de rechazo en el diálogo.

### 7.6. Ver detalle de lead

Muestra:

- Datos de la empresa y contacto
- Dirección e información fiscal
- Notas
- Estado y motivo de rechazo (si aplica)
- Información de Odoo CRM (ID de oportunidad, ID de partner si ya se creó)

**Acciones disponibles:**

| Estado | Acciones |
|---|---|
| Pendiente | Editar, Eliminar |
| Aprobado | Crear cliente, Crear cotización |
| Sincronizado | Refrescar estado desde Odoo |

### 7.7. Crear cliente desde lead aprobado

Una vez aprobado, puede crear el cliente en Odoo desde el detalle del lead. El sistema:

1. Crea el partner en Odoo.
2. Lo sincroniza a la base local.
3. Asocia el lead al nuevo cliente.

### 7.8. Crear cotización desde lead aprobado

Después de crear el cliente, puede generar una cotización directamente desde el lead. El sistema:

1. Crea el cliente en Odoo (si no se creó antes).
2. Abre la pantalla de nueva cotización con el cliente preseleccionado.

---

## 8. Administración

### 8.1. Sincronizar datos desde Odoo

Acceda desde el **Perfil de usuario** (solo administradores).

**Sincronizar clientes:**
Trae todos los clientes desde Odoo (`res.partner`). Los clientes existentes se actualizan; los nuevos se agregan. También sincroniza los contactos asociados.

**Sincronizar productos:**
Trae productos activos e impuestos desde Odoo. Los precios se toman de la lista de precios USD.

> La sincronización se ejecuta en segundo plano. Recibirá una confirmación inmediata y los datos se actualizarán progresivamente.

### 8.2. Asignar vendedor interno a usuarios

Cada usuario de la app puede tener un **vendedor interno** asociado. Este se utiliza al crear leads en Odoo CRM para asignar el responsable de la oportunidad.

**Para asignarlo:**

1. Ejecute la siguiente consulta en el **SQL Editor de Supabase**:

```sql
UPDATE users SET vendedor_interno = 'Nombre del vendedor' WHERE id = <user_id>;
```

Reemplace `'Nombre del vendedor'` con el nombre o login del usuario en Odoo que será el responsable interno.

> Próximamente: interfaz de administración de usuarios desde la app.

---

## 9. Solución de Problemas

### 9.1. No puedo iniciar sesión

- Verifique que el email y la contraseña sean correctos.
- Si olvidó su contraseña, contacte al administrador.

### 9.2. Los clientes no aparecen

- Verifique que el administrador haya ejecutado la **sincronización de clientes** desde su perfil.
- Si es un vendedor, solo ve los clientes donde es el vendedor externo asignado.

### 9.3. Error al sincronizar

- Verifique que el servicio de Odoo esté disponible.
- Contacte al administrador si el error persiste.

### 9.4. Error al enviar lead a Odoo

| Error | Causa | Solución |
|---|---|---|
| "Ya existe un cliente con ese CUIT" | El CUIT ya está registrado | Verifique que el CUIT sea correcto |
| "Token inválido o expirado" | Token de Odoo desactualizado | El admin debe actualizar el token en Railway |
| "Invalid field" | Campo de Odoo incorrecto | Contacte al administrador |

### 9.5. La cotización no se genera

- Verifique que tenga al menos un producto agregado.
- Verifique que el cliente esté seleccionado.
- Si el error persiste, contacte al administrador.

### 9.6. Contacto

Para reportar errores o solicitar ayuda:

- Email: [informatica@belenergy.com.ar](mailto:informatica@belenergy.com.ar)
- Sistema de tickets: [https://github.com/pablojgarcia/Belenergy-Ventas/issues](https://github.com/pablojgarcia/Belenergy-Ventas/issues)
