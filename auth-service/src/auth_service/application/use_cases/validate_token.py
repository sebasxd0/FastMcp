from datetime import datetime, timezone

from auth_service.domain.entities.user import User
from auth_service.domain.exceptions import InvalidTokenError
from auth_service.domain.repositories.token_repository import TokenRepository
from auth_service.domain.repositories.user_repository import UserRepository
from auth_service.domain.services.token_service import TokenService


class ValidateToken:
    def __init__(
        self,
        token_service: TokenService,
        token_repository: TokenRepository,
        user_repository: UserRepository,
    ):
        self.token_service = token_service
        self.token_repository = token_repository
        self.user_repository = user_repository

    def execute(self, encoded_token: str) -> User:
        claims = self.token_service.decode_token(encoded_token)
        now = datetime.now(timezone.utc)
        if claims is None or not self.token_repository.is_active(claims, now):
            raise InvalidTokenError("Invalid or expired token")
        user = self.user_repository.get_user_by_id(claims.user_id)
        if user is None:
            raise InvalidTokenError("Invalid or expired token")
        return user