from datetime import datetime, timezone

from auth_service.domain.exceptions import InvalidTokenError
from auth_service.domain.repositories.token_repository import TokenRepository
from auth_service.domain.services.token_service import TokenService


class RefreshToken:
    def __init__(self, token_service: TokenService, token_repository: TokenRepository):
        self.token_service = token_service
        self.token_repository = token_repository

    def execute(self, encoded_token: str) -> str:
        claims = self.token_service.decode_token(encoded_token)
        now = datetime.now(timezone.utc)
        if claims is None or not self.token_repository.revoke(claims, now):
            raise InvalidTokenError("Invalid or expired token")

        issued_token = self.token_service.issue_token(claims.user_id)
        self.token_repository.save(issued_token.claims)
        return issued_token.encoded_token