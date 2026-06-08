# Estado Actual de Belenergy-Ventas

Este documento detalla el estado funcional actual del repositorio de Belenergy-Ventas.

## Backend
- **Framework:** FastAPI (Python)
- **Base de datos:** Utiliza SQLAlchemy ORM.
- **Verificación de salud:** Proporciona un endpoint `/health` básico.
- **Funcionalidad:** Sirve principalmente para propósitos de autenticación en esta etapa.

## Frontend
- **Framework:** Flutter (compatible con Web)
- **Funcionalidades:** 
    - Pantalla de inicio de sesión: Incluye campos de correo/contraseña, validación, manejo de errores a través de `AuthProvider` y retroalimentación visual (indicadores de carga, mensajes de error).
    - Navegación: Configuración básica de enrutamiento con una pantalla de inicio (splash), pantalla de inicio de sesión y pantalla principal.
    - Recursos: Incluye recursos gráficos de la marca (logo de Belenergy ARG).

## Autenticación
- **Backend:** 
    - Endpoints: `/auth/register` (POST), `/auth/login` (POST), `/auth/me` (GET, protegido).
    - Lógica: Implementa hashing de contraseñas y autenticación basada en JWT con tiempo de expiración.
- **Frontend:** 
    - Gestiona el estado de autenticación a través de `AuthProvider`.
    - Maneja el flujo de inicio de sesión del usuario y la lógica de gestión persistente de la sesión.

## Infraestructura
- **Contenedores:** Dockerfile presente en el directorio `Backend` y `docker-compose.yml` en la raíz, facilitando el despliegue contenedorizado.
