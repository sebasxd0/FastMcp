from datetime import datetime, timezone

from auth_service.domain.entities.user import User
from auth_service.domain.exceptions import InvalidUserDataError
from auth_service.domain.repositories.user_repository import UserRepository
from auth_service.domain.services.password_hasher import PasswordHasher


class CreateUser:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, username: str, password: str) -> User:
        normalized_username = username.strip()
        if not 3 <= len(normalized_username) <= 50 or not 8 <= len(password) <= 128:
            raise InvalidUserDataError("Username or password does not meet length requirements")

        user = User(
            id=None,
            username=normalized_username,
            hashed_password=self.password_hasher.hash_password(password),
            created_at=datetime.now(timezone.utc),
        )
        return self.user_repository.save_user(user)