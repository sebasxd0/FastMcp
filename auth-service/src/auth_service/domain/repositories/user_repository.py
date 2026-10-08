from abc import ABC, abstractmethod

from auth_service.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def save_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_username(self, username: str) -> User | None:
        raise NotImplementedError