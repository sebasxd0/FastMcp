from abc import ABC, abstractmethod
from datetime import datetime

from auth_service.domain.services.token_service import TokenClaims


class TokenRepository(ABC):
    @abstractmethod
    def save(self, claims: TokenClaims) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_active(self, claims: TokenClaims, now: datetime) -> bool:
        raise NotImplementedError

    @abstractmethod
    def revoke(self, claims: TokenClaims, now: datetime) -> bool:
        raise NotImplementedError