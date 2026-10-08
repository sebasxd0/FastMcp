from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class TokenClaims:
    user_id: int
    token_id: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class IssuedToken:
    encoded_token: str
    claims: TokenClaims


class TokenService(Protocol):
    def issue_token(self, user_id: int) -> IssuedToken:
        ...

    def decode_token(self, encoded_token: str) -> TokenClaims | None:
        ...