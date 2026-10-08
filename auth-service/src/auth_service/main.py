from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from auth_service.config import Settings
from auth_service.infrastructure.database.connection import Database
from auth_service.infrastructure.security.jwt_service import JWTService
from auth_service.presentation.http.routes.auth import router as auth_router


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings()
    database = Database(app_settings.database_path)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        database.initialize()
        yield

    app = FastAPI(title="Authentication Service", version="0.1.0", lifespan=lifespan)
    app.state.database = database
    app.state.jwt_service = JWTService(
        secret_key=app_settings.jwt_secret_key,
        algorithm=app_settings.jwt_algorithm,
    )
    app.include_router(auth_router)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()