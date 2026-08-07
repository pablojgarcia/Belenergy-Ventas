# Manual de Usuario — Belenergy Ventas

Sistema de gestión de ventas y cotizaciones integrado con **Odoo v19**.

---

## Índice

1. [Introducción](#1-introducción)
2. [Acceso y Autenticación](#2-acceso-y-autenticación)
3. [Dashboard / Inicio](#3-dashboard--inicio)
4. [Clientes](#4-clientes)
5. [Productos](#5-productos)
6. [Cotizaciones](#6-cotizaciones)
7. [Administración](#7-administración)
8. [Solución de Problemas](#8-solución-de-problemas)

---

## 1. Introducción

**Belenergy Ventas** es una aplicación web para la gestión de clientes, cotizaciones y productos, sincronizada en tiempo real con Odoo v19.

**URL de acceso:** [https://solarapp-production.up.railway.app](https://solarapp-production.up.railway.app)

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
   - Si el cliente es **nuevo** (no figura en la búsqueda), presione **Nuevo cliente** en el buscador.
3. **Cliente nuevo** (opcional):
   - Se muestra un panel editable con **Razón social** (obligatorio) y **CUIT** (opcional).
   - El CUIT se valida con el algoritmo oficial de AFIP (módulo 11). Si no lo conoce, puede omitirlo.
   - El cliente se crea automáticamente en Odoo **al generar la cotización**.
   - Puede volver a un cliente existente con **Seleccionar cliente existente**.
4. **Agregar productos:**
   - Presione **Agregar producto**.
   - Busque por nombre, código o código de barras.
   - Seleccione el producto; se agrega a la tabla con cantidad 1.
   - Ajuste la cantidad con los botones ➕/➖.
   - Puede eliminar un renglón con el botón **✕**.
5. **Notas:** (opcional) agregue una descripción interna.
6. **Guardar:** presione **Guardar** para guardar el borrador.
7. **Generar:** presione **Generar cotización** para crear el cliente nuevo (si corresponde) y la orden de venta en Odoo.

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

## 7. Administración

### 7.1. Sincronizar datos desde Odoo

Acceda desde el **Perfil de usuario** (solo administradores).

**Sincronizar clientes:**
Trae todos los clientes desde Odoo (`res.partner`). Los clientes existentes se actualizan; los nuevos se agregan. También sincroniza los contactos asociados.

**Sincronizar productos:**
Trae productos activos e impuestos desde Odoo. Los precios se toman de la lista de precios USD.

> La sincronización se ejecuta en segundo plano. Recibirá una confirmación inmediata y los datos se actualizarán progresivamente.

### 7.2. Asignar vendedor interno a usuarios

Cada usuario de la app puede tener un **vendedor interno** asociado. Este se utiliza en la sincronización de clientes para asignar el responsable en Odoo.

**Para asignarlo:**

1. Ejecute la siguiente consulta en el **SQL Editor de Supabase**:

```sql
UPDATE users SET vendedor_interno = 'Nombre del vendedor' WHERE id = <user_id>;
```

Reemplace `'Nombre del vendedor'` con el nombre o login del usuario en Odoo que será el responsable interno.

> Próximamente: interfaz de administración de usuarios desde la app.

---

## 8. Solución de Problemas

### 8.1. No puedo iniciar sesión

- Verifique que el email y la contraseña sean correctos.
- Si olvidó su contraseña, contacte al administrador.

### 8.2. Los clientes no aparecen

- Verifique que el administrador haya ejecutado la **sincronización de clientes** desde su perfil.
- Si es un vendedor, solo ve los clientes donde es el vendedor externo asignado.

### 8.3. Error al sincronizar

- Verifique que el servicio de Odoo esté disponible.
- Contacte al administrador si el error persiste.

### 8.4. Error al crear un cliente nuevo

| Error | Causa | Solución |
|---|---|---|
| "El CUIT ingresado no es válido" | El CUIT no cumple el algoritmo de AFIP | Verifique que el CUIT sea correcto (11 dígitos) |
| "Ya existe un cliente con ese CUIT" | El CUIT ya está registrado localmente | Verifique que el CUIT sea correcto o use el cliente existente |
| "Ya existe un cliente con ese CUIT en Odoo" | El CUIT ya existe en Odoo | Use el cliente existente |
| "Token inválido o expirado" | Token de Odoo desactualizado | El admin debe actualizar el token en Railway |
| "Invalid field" | Campo de Odoo incorrecto | Contacte al administrador |

### 8.5. La cotización no se genera

- Verifique que tenga al menos un producto agregado.
- Verifique que el cliente esté seleccionado (o la razón social del cliente nuevo esté completa).
- Si el error persiste, contacte al administrador.

### 8.6. Contacto

Para reportar errores o solicitar ayuda:

- Email: [informatica@belenergy.com.ar](mailto:informatica@belenergy.com.ar)
- Sistema de tickets: [https://github.com/pablojgarcia/Belenergy-Ventas/issues](https://github.com/pablojgarcia/Belenergy-Ventas/issues)
