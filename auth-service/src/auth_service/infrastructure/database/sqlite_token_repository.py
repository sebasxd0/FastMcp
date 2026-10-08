from datetime import datetime

from auth_service.domain.repositories.token_repository import TokenRepository
from auth_service.domain.services.token_service import TokenClaims
from auth_service.infrastructure.database.connection import Database


class SQLiteTokenRepository(TokenRepository):
    def __init__(self, database: Database):
        self.database = database

    def save(self, claims: TokenClaims) -> None:
        with self.database.connection() as connection:
            connection.execute(
                "INSERT INTO tokens (token_id, user_id, expires_at) VALUES (?, ?, ?)",
                (claims.token_id, claims.user_id, int(claims.expires_at.timestamp())),
            )

    def is_active(self, claims: TokenClaims, now: datetime) -> bool:
        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT 1 FROM tokens
                WHERE token_id = ? AND user_id = ? AND revoked_at IS NULL AND expires_at > ?
                """,
                (claims.token_id, claims.user_id, int(now.timestamp())),
            ).fetchone()
        return row is not None

    def revoke(self, claims: TokenClaims, now: datetime) -> bool:
        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tokens SET revoked_at = ?
                WHERE token_id = ? AND user_id = ? AND revoked_at IS NULL AND expires_at > ?
                """,
                (
                    int(now.timestamp()),
                    claims.token_id,
                    claims.user_id,
                    int(now.timestamp()),
                ),
            )
        return cursor.rowcount == 1