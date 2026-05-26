# SolarApp — Flutter

Aplicación mobile de ventas de equipos fotovoltaicos con backend Python/Odoo.

## Estructura del proyecto

```
lib/
├── main.dart                    # Entry point
├── models/
│   └── auth_model.dart          # AuthToken, UserInfo
├── screens/
│   ├── splash_screen.dart       # Verificación de sesión al inicio
│   ├── login_screen.dart        # Pantalla de login con JWT
│   └── home_screen.dart         # Pantalla principal con menú
├── services/
│   ├── auth_service.dart        # Lógica JWT, secure storage, Dio
│   └── auth_provider.dart       # Estado global con Provider
├── widgets/
│   ├── menu_card.dart           # Card del menú de módulos
│   └── stat_card.dart           # Card de estadísticas
└── utils/
    └── theme.dart               # Colores, tipografía, tema global
```

## Setup

### 1. Instalar dependencias

```bash
flutter pub get
```

### 2. Configurar la URL del backend

En `lib/services/auth_service.dart`, línea 6:

```dart
static const String _baseUrl = 'https://tu-backend.com/api'; // ← Cambiar
```

### 3. Endpoints esperados del backend Python (FastAPI)

| Método | Ruta             | Descripción                        |
|--------|------------------|------------------------------------|
| POST   | `/auth/login`    | Recibe `username` + `password`, devuelve tokens JWT |
| POST   | `/auth/refresh`  | Recibe `refresh_token`, devuelve nuevos tokens |
| GET    | `/auth/me`       | Devuelve info del usuario autenticado |

#### Respuesta esperada de `/auth/login`:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Respuesta esperada de `/auth/me`:
```json
{
  "id": 1,
  "name": "Pablo García",
  "email": "pablo@empresa.com",
  "role": "Vendedor",
  "avatar_url": null
}
```

### 4. Correr la app

```bash
flutter run
```

## Módulos del menú (listos para conectar)

- **Presupuestos** — Crear y gestionar cotizaciones
- **Productos** — Catálogo FV (paneles, inversores, baterías)
- **Clientes** — Cartera de clientes
- **Pedidos** — Órdenes activas en Odoo
- **Reportes** — Ventas y métricas
- **Stock** — Inventario sincronizado con Odoo
- **Instalaciones** — Seguimiento de proyectos
- **Soporte** — Post-venta y garantías

## Próximos pasos sugeridos

1. Implementar `go_router` para navegación entre pantallas
2. Agregar `dio interceptors` para inyectar el token en cada request automáticamente
3. Conectar cada módulo con su endpoint Odoo correspondiente
4. Agregar `hive` o `sqflite` para caché offline
