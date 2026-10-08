from auth_service.domain.exceptions import InvalidCredentialsError
from auth_service.domain.repositories.user_repository import UserRepository
from auth_service.domain.services.password_hasher import PasswordHasher


class ValidateUser:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, username: str, password: str):
        user = self.user_repository.get_user_by_username(username.strip())
        if user is None or not self.password_hasher.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid username or password")
        return user