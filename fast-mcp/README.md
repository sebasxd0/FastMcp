# fast-mcp

Servidor MCP (FastMCP) con transporte HTTP, protegido con los tokens JWT emitidos por `auth-service`.

## Autenticación

Este servidor no gestiona usuarios propios: valida cada llamada contra el endpoint
`POST /auth/validate` del servicio `auth-service` (carpeta `../auth-service`). El cliente MCP
debe enviar `Authorization: Bearer <token>` con un token obtenido en `auth-service`.

Variable de entorno `AUTH_SERVICE_URL` (por defecto `http://127.0.0.1:8001`) apunta a la URL base de `auth-service`.

### 1. Levantar auth-service (puerto distinto al de fast-mcp)

```powershell
cd ../auth-service
uv run uvicorn auth_service.main:app --port 8001
```

### 2. Generar usuario y contraseña, y obtener el token

```powershell
curl.exe -s -X POST http://127.0.0.1:8001/auth/register -H "Content-Type: application/json" -d '{"username":"demo","password":"demo12345"}'
curl.exe -s -X POST http://127.0.0.1:8001/auth/login -H "Content-Type: application/json" -d '{"username":"demo","password":"demo12345"}'
```

El `login` devuelve `access_token`: ese es el token que debe enviarse al llamar `fast-mcp`.

### 3. Levantar fast-mcp

```powershell
uv run python src/main.py
```

### 4. Llamar una tool incluyendo el token en cada petición

```powershell
curl.exe -s -i -X POST http://127.0.0.1:8000/mcp `
  -H "Content-Type: application/json" `
  -H "Accept: application/json, text/event-stream" `
  -H "Authorization: Bearer <access_token>" `
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl-test","version":"1.0.0"}}}'
```

Sin un token válido emitido por `auth-service`, el servidor responde `401 Unauthorized`.
