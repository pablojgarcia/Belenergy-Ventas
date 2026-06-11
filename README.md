# Belenergy

Proyecto monorepo para la solución de ventas de equipos fotovoltaicos.
Incluye un backend en FastAPI y un cliente móvil/web en Flutter.

## Estructura del proyecto

- `Backend/`
  - API REST construida con FastAPI.
  - `requirements.txt` con dependencias Python.
  - `Dockerfile` para construir la imagen del backend.
  - `app/` contiene el código de la API, autenticación JWT y modelo de usuario.

- `Ventas/`
  - Aplicación Flutter (`solarapp`).
  - `pubspec.yaml` define paquetes: `dio`, `provider`, `flutter_secure_storage`, `jwt_decoder`, etc.
  - `lib/` contiene lógica de UI, servicios y configuración.

## Arquitectura

### Backend

- **FastAPI** para la API.
- **SQLAlchemy** para el ORM.
- **JWT** para autenticación y protección de rutas.
- **PostgreSQL** o cualquier base de datos compatible con SQLAlchemy, configurada mediante `DATABASE_URL`.
- Rutas clave:
  - `POST /auth/register` registra usuarios.
  - `POST /auth/login` devuelve `access_token`.
  - `GET /auth/me` devuelve datos del usuario autenticado.
  - `GET /health` salud del servicio.

### Frontend

- **Flutter** con `provider` para estado.
- **Dio** para llamadas HTTP.
- **flutter_secure_storage** para guardar tokens de acceso.
- **jwt_decoder** para validar expiración del token.
- Modo de desarrollo: `Ventas/lib/config/app_config.dart` controla `bypassAuthentication`.
- Servicio de autenticación: `Ventas/lib/services/auth_service.dart`.

## Configuración local

### Pre-requisitos

- Python 3.12
- pip
- Flutter SDK (`flutter`) instalado
- Postman/Insomnia opcional para probar la API
- PostgreSQL local o remoto disponible

### Backend

1. Entrar al backend:
```bash
cd Backend
```

2. Crear el entorno virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
export DATABASE_URL="postgresql://usuario:password@localhost:5432/belenergy"
export SECRET_KEY="una_clave_segura"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> Nota: `DATABASE_URL` es obligatoria para que SQLAlchemy conecte con la base de datos.

5. Ejecutar el servidor en modo desarrollo:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Verificar que funcione:
```bash
curl http://127.0.0.1:8000/health
```

### Backend con Docker

1. Construir la imagen:
```bash
cd Backend
docker build -t belenergy-backend .
```

2. Ejecutar el contenedor:
```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql://usuario:password@host:5432/belenergy" \
  -e SECRET_KEY="una_clave_segura" \
  belenergy-backend
```

### Frontend

1. Entrar al proyecto Flutter:
```bash
cd Ventas
```

2. Instalar paquetes:
```bash
flutter pub get
```

3. Configurar el backend:
- Abrir `Ventas/lib/services/auth_service.dart`
- Cambiar `static const String _baseUrl = 'https://tu-backend.com/api';`
  por la URL local del backend, por ejemplo:
  `http://127.0.0.1:8000`
- Si usas modo de desarrollo para no depender del backend, revisa `Ventas/lib/config/app_config.dart`.

4. Ejecutar la app:
```bash
flutter run
```

Para Web:
```bash
flutter run -d chrome
```

## Depuración

### Backend

- Usa `uvicorn` con `--reload` para recarga automática.
- Monitorea la consola para errores de importación, conexión a la base de datos o JWT.
- Comprueba la variable `DATABASE_URL` y que coincida con la base de datos en ejecución.
- Prueba los endpoints con `curl`, Postman o Insomnia.
- Si el token falla, revisa `SECRET_KEY` y `ALGORITHM`.
- Para depurar en VS Code, crea una configuración de lanzamiento que ejecute `uvicorn app.main:app --reload`.

### Frontend

- Usa `flutter run --debug` o el depurador de VS Code/Android Studio.
- En el modo de desarrollo, `bypassAuthentication` permite trabajar sin backend.
- Revisa los logs de `Dio` en `auth_service.dart` y los mensajes de error en la UI.
- Si no inicia en el dispositivo, verifica que `flutter doctor` esté limpio.
- Cuando cambies la URL del backend, limpia la caché de Flutter si es necesario:
```bash
flutter clean
flutter pub get
```

## Consejos

- No subas credenciales ni `.env` al repositorio.
- Usa `.gitignore` para excluir `build/`, `.dart_tool/`, `.venv/`, `*.pyc`, `*.iml` y archivos temporales.
- Si trabajas en equipo, documenta en el README las URLs locales y variables necesarias.
- Mantén separados los entornos: local, staging y producción.

## Archivos clave

- `Backend/app/main.py`
- `Backend/app/auth.py`
- `Backend/app/dependencies.py`
- `Backend/app/database.py`
- `Ventas/lib/main.dart`
- `Ventas/lib/services/auth_service.dart`
- `Ventas/lib/config/app_config.dart`


