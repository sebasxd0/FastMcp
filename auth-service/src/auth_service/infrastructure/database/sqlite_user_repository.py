import sqlite3
from datetime import datetime, timezone

from auth_service.domain.entities.user import User
from auth_service.domain.exceptions import UserAlreadyExistsError
from auth_service.domain.repositories.user_repository import UserRepository
from auth_service.infrastructure.database.connection import Database


class SQLiteUserRepository(UserRepository):
    def __init__(self, database: Database):
        self.database = database

    def save_user(self, user: User) -> User:
        created_at = datetime.now(timezone.utc)
        try:
            with self.database.connection() as connection:
                cursor = connection.execute(
                    "INSERT INTO users (username, hashed_password, created_at) VALUES (?, ?, ?)",
                    (user.username, user.hashed_password, created_at.isoformat()),
                )
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError as error:
            raise UserAlreadyExistsError("Username already exists") from error
        return User(user_id, user.username, user.hashed_password, created_at)

    def get_user_by_id(self, user_id: int) -> User | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT id, username, hashed_password, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return self._to_user(row) if row else None

    def get_user_by_username(self, username: str) -> User | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT id, username, hashed_password, created_at FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return self._to_user(row) if row else None

    @staticmethod
    def _to_user(row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            username=row["username"],
            hashed_password=row["hashed_password"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )