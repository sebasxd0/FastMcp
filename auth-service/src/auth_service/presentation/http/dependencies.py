from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth_service.application.use_cases.create_token import CreateToken
from auth_service.application.use_cases.create_user import CreateUser
from auth_service.application.use_cases.refresh_token import RefreshToken
from auth_service.application.use_cases.validate_token import ValidateToken
from auth_service.application.use_cases.validate_user import ValidateUser
from auth_service.domain.entities.user import User
from auth_service.domain.repositories.token_repository import TokenRepository
from auth_service.domain.repositories.user_repository import UserRepository
from auth_service.infrastructure.database.connection import Database
from auth_service.infrastructure.database.sqlite_token_repository import SQLiteTokenRepository
from auth_service.infrastructure.database.sqlite_user_repository import SQLiteUserRepository
from auth_service.infrastructure.security.jwt_service import JWTService
from auth_service.infrastructure.security.password_hasher import PasswordHasher

bearer_scheme = HTTPBearer(auto_error=False)


def get_database(request: Request) -> Database:
    return request.app.state.database


def get_user_repository(database: Database = Depends(get_database)) -> UserRepository:
    return SQLiteUserRepository(database)


def get_token_repository(database: Database = Depends(get_database)) -> TokenRepository:
    return SQLiteTokenRepository(database)


def get_jwt_service(request: Request) -> JWTService:
    return request.app.state.jwt_service


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_create_user(
    repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> CreateUser:
    return CreateUser(repository, password_hasher)


def get_validate_user(
    repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> ValidateUser:
    return ValidateUser(repository, password_hasher)


def get_create_token(
    token_service: JWTService = Depends(get_jwt_service),
    token_repository: TokenRepository = Depends(get_token_repository),
) -> CreateToken:
    return CreateToken(token_service, token_repository)


def get_validate_token(
    token_service: JWTService = Depends(get_jwt_service),
    token_repository: TokenRepository = Depends(get_token_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> ValidateToken:
    return ValidateToken(token_service, token_repository, user_repository)


def get_refresh_token(
    token_service: JWTService = Depends(get_jwt_service),
    token_repository: TokenRepository = Depends(get_token_repository),
) -> RefreshToken:
    return RefreshToken(token_service, token_repository)


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )