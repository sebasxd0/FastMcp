import os

import httpx
import truststore
from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, TokenVerifier

truststore.inject_into_ssl()

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://127.0.0.1:8001")


class AuthServiceTokenVerifier(TokenVerifier):
    """Valida los tokens Bearer contra el endpoint /auth/validate de auth-service."""

    async def verify_token(self, token: str) -> AccessToken | None:
        async with httpx.AsyncClient(base_url=AUTH_SERVICE_URL) as client:
            try:
                response = await client.post(
                    "/auth/validate",
                    headers={"Authorization": f"Bearer {token}"},
                )
            except httpx.HTTPError:
                return None
        if response.status_code != 200:
            return None
        user = response.json()["user"]
        return AccessToken(
            token=token,
            client_id=str(user["id"]),
            scopes=[],
            subject=user["username"],
        )


mcp = FastMCP("MyFirstApp", auth=AuthServiceTokenVerifier())

FRANKFURTER_BASE_URL = "https://api.frankfurter.dev/v1"


@mcp.tool
def greet(name: str):
    return f"Hello, {name} !"


@mcp.tool
def get_exchange_rate(currency_from: str, currency_to: str, currency_date: str = "latest") -> dict:
    """
    Obtiene el tipo de cambio entre dos monedas usando la API v1 de Frankfurter.

    Esta herramienta consulta el endpoint https://api.frankfurter.dev/v1/{currency_date}
    con los parámetros `base` (currency_from) y `symbols` (currency_to), tal como se
    describe en la documentación oficial: https://frankfurter.dev/es/v1/

    Args:
        currency_from: Código ISO 4217 de la moneda de origen (ej. "USD", "EUR").
        currency_to: Código ISO 4217 de la moneda de destino (ej. "COP", "JPY").
        currency_date: Fecha de la cotización en formato "YYYY-MM-DD", o "latest"
            (valor por defecto) para obtener la tasa más reciente disponible.

    Returns:
        dict con la respuesta cruda de Frankfurter, por ejemplo:
        {
            "amount": 1.0,
            "base": "USD",
            "date": "2024-01-01",
            "rates": {"COP": 3900.12}
        }

    Errores:
        Lanza httpx.HTTPStatusError si la API responde con un código de error
        (por ejemplo, código de moneda inválido o fecha no soportada).
    """
    url = f"{FRANKFURTER_BASE_URL}/{currency_date}"
    params = {
        "base": currency_from.upper(),
        "symbols": currency_to.upper(),
    }
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)

