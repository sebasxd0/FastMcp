# Authentication Service

Servicio HTTP de autenticacion con FastAPI, Python 3.12, UV y SQLite. La estructura separa dominio, casos de uso, infraestructura y presentacion.

## Inicio rapido

```powershell
uv sync
Copy-Item .env.example .env
uv run uvicorn auth_service.main:app --reload
```

La base SQLite se crea automaticamente en `users.db`. Configura `DATABASE_PATH`, `JWT_SECRET_KEY` y `JWT_ALGORITHM` en `.env`; usa una clave secreta propia de al menos 32 caracteres fuera del entorno local. La documentacion HTTP queda disponible en `http://127.0.0.1:8000/docs`.

## Endpoints

- `POST /auth/register`: crea un usuario. Username de 3 a 50 caracteres y password de 8 a 128.
- `POST /auth/login`: verifica credenciales y entrega un JWT bearer con expiracion de una hora.
- `POST /auth/validate`: valida firma, expiracion, usuario y estado activo del token.
- `POST /auth/refresh`: rota un token activo; el token anterior queda revocado y ya no puede reutilizarse. Solo se puede refrescar antes de su expiracion.
- `GET /health`: comprobacion de disponibilidad.

`/auth/validate` y `/auth/refresh` reciben el token en `Authorization: Bearer <token>`. Usuarios y registros de tokens, incluidos su vencimiento y revocacion, se guardan en SQLite. Las contrasenas se almacenan con Argon2.

## Pruebas

```powershell
uv run pytest
```

Los tests cubren casos positivos y negativos, limites de entrada, tokens expirados, duplicados y rotacion de tokens.