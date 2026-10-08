from datetime import timezone

import pytest

from auth_service.application.use_cases.create_user import CreateUser
from auth_service.domain.entities.user import User
from auth_service.domain.exceptions import InvalidUserDataError, UserAlreadyExistsError
from auth_service.domain.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users = {}

    def save_user(self, user: User) -> User:
        if user.username.lower() in self.users:
            raise UserAlreadyExistsError("Username already exists")
        saved_user = User(
            id=len(self.users) + 1,
            username=user.username,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
        self.users[user.username.lower()] = saved_user
        return saved_user

    def get_user_by_id(self, user_id: int) -> User | None:
        return next((user for user in self.users.values() if user.id == user_id), None)

    def get_user_by_username(self, username: str) -> User | None:
        return self.users.get(username.lower())


class FakePasswordHasher:
    def hash_password(self, password: str) -> str:
        return f"hashed:{password}"


@pytest.fixture
def create_user():
    return CreateUser(InMemoryUserRepository(), FakePasswordHasher())


def test_create_user_hashes_password_and_normalizes_username(create_user):
    user = create_user.execute("  alice  ", "password123")

    assert user.id == 1
    assert user.username == "alice"
    assert user.hashed_password == "hashed:password123"
    assert user.created_at.tzinfo == timezone.utc


@pytest.mark.parametrize(
    ("username", "password"),
    [("ab", "password123"), ("a" * 51, "password123"), ("alice", "short"), ("alice", "p" * 129)],
)
def test_create_user_rejects_values_outside_boundaries(create_user, username, password):
    with pytest.raises(InvalidUserDataError):
        create_user.execute(username, password)


def test_create_user_accepts_maximum_username_and_password_lengths(create_user):
    user = create_user.execute("u" * 50, "p" * 128)

    assert len(user.username) == 50


def test_create_user_rejects_duplicate_username(create_user):
    create_user.execute("alice", "password123")

    with pytest.raises(UserAlreadyExistsError):
        create_user.execute("ALICE", "password123")