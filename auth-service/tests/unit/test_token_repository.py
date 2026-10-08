from datetime import datetime, timedelta, timezone

from auth_service.domain.entities.user import User
from auth_service.domain.services.token_service import TokenClaims
from auth_service.infrastructure.database.connection import Database
from auth_service.infrastructure.database.sqlite_token_repository import SQLiteTokenRepository
from auth_service.infrastructure.database.sqlite_user_repository import SQLiteUserRepository


def test_token_is_inactive_at_exact_expiration_boundary(tmp_path):
    database = Database(tmp_path / "tokens.db")
    database.initialize()
    user = SQLiteUserRepository(database).save_user(
        User(None, "alice", "hash", datetime.now(timezone.utc))
    )
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    claims = TokenClaims(user.id, "token-id", expires_at)
    repository = SQLiteTokenRepository(database)
    repository.save(claims)

    assert repository.is_active(claims, expires_at - timedelta(seconds=1))
    assert not repository.is_active(claims, expires_at)


def test_revoked_token_cannot_be_used_again(tmp_path):
    database = Database(tmp_path / "tokens.db")
    database.initialize()
    user = SQLiteUserRepository(database).save_user(
        User(None, "alice", "hash", datetime.now(timezone.utc))
    )
    now = datetime.now(timezone.utc)
    claims = TokenClaims(user.id, "token-id", now + timedelta(hours=1))
    repository = SQLiteTokenRepository(database)
    repository.save(claims)

    assert repository.revoke(claims, now)
    assert not repository.revoke(claims, now)
    assert not repository.is_active(claims, now)