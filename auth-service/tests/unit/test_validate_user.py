from datetime import datetime, timezone

import pytest

from auth_service.application.use_cases.validate_user import ValidateUser
from auth_service.domain.entities.user import User
from auth_service.domain.exceptions import InvalidCredentialsError
from auth_service.domain.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self, user=None):
        self.user = user

    def save_user(self, user: User) -> User:
        self.user = user
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.user if self.user and self.user.id == user_id else None

    def get_user_by_username(self, username: str) -> User | None:
        return self.user if self.user and self.user.username == username else None


class FakePasswordHasher:
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return password == "correct-password" and hashed_password == "stored-hash"


@pytest.fixture
def validate_user():
    user = User(1, "alice", "stored-hash", datetime.now(timezone.utc))
    return ValidateUser(InMemoryUserRepository(user), FakePasswordHasher())


def test_validate_user_returns_user_for_valid_credentials(validate_user):
    assert validate_user.execute("alice", "correct-password").id == 1


@pytest.mark.parametrize(
    ("username", "password"),
    [("unknown", "correct-password"), ("alice", "incorrect-password")],
)
def test_validate_user_rejects_invalid_credentials(validate_user, username, password):
    with pytest.raises(InvalidCredentialsError):
        validate_user.execute(username, password)