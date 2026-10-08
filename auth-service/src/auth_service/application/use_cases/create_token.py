from auth_service.domain.repositories.token_repository import TokenRepository
from auth_service.domain.services.token_service import TokenService


class CreateToken:
    def __init__(self, token_service: TokenService, token_repository: TokenRepository):
        self.token_service = token_service
        self.token_repository = token_repository

    def execute(self, user_id: int) -> str:
        issued_token = self.token_service.issue_token(user_id)
        self.token_repository.save(issued_token.claims)
        return issued_token.encoded_token