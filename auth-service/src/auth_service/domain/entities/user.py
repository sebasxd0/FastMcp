from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    id: int | None
    username: str
    hashed_password: str
    created_at: datetime