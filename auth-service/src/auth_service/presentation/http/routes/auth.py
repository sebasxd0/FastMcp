from fastapi import APIRouter, Depends, HTTPException, status

from auth_service.application.schemas.auth import (
    TokenResponse,
    TokenValidationResponse,
    UserCreateRequest,
    UserResponse,
)
from auth_service.application.use_cases.create_token import CreateToken
from auth_service.application.use_cases.create_user import CreateUser
from auth_service.application.use_cases.refresh_token import RefreshToken
from auth_service.application.use_cases.validate_token import ValidateToken
from auth_service.application.use_cases.validate_user import ValidateUser
from auth_service.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from auth_service.presentation.http.dependencies import (
    get_bearer_token,
    get_create_token,
    get_create_user,
    get_refresh_token,
    get_validate_token,
    get_validate_user,
    unauthorized,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: UserCreateRequest,
    create_user: CreateUser = Depends(get_create_user),
) -> UserResponse:
    try:
        user = create_user.execute(request.username, request.password)
    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return UserResponse(id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
def login(
    request: UserCreateRequest,
    validate_user: ValidateUser = Depends(get_validate_user),
    create_token: CreateToken = Depends(get_create_token),
) -> TokenResponse:
    try:
        user = validate_user.execute(request.username, request.password)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    return TokenResponse(access_token=create_token.execute(user.id))


@router.post("/validate", response_model=TokenValidationResponse)
def validate_token(
    encoded_token: str = Depends(get_bearer_token),
    use_case: ValidateToken = Depends(get_validate_token),
) -> TokenValidationResponse:
    try:
        user = use_case.execute(encoded_token)
    except InvalidTokenError as error:
        raise unauthorized() from error
    return TokenValidationResponse(user=UserResponse(id=user.id, username=user.username))


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    encoded_token: str = Depends(get_bearer_token),
    use_case: RefreshToken = Depends(get_refresh_token),
) -> TokenResponse:
    try:
        refreshed_token = use_case.execute(encoded_token)
    except InvalidTokenError as error:
        raise unauthorized() from error
    return TokenResponse(access_token=refreshed_token)