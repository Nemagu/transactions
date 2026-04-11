"""Фабрика создания и восстановления сущностей пользователя."""

from uuid import UUID

from src.domain.user.entity import User
from src.domain.user.value_objects import (
    FirstName,
    LastName,
    UserID,
    UserState,
    UserStatus,
)
from src.domain.value_objects import Version


class UserFactory:
    """Фабрика для создания новых и восстановленных пользователей."""

    @staticmethod
    def new(user_id: UUID, first_name: str, last_name: str) -> User:
        """
        Args:
            user_id (UUID): Идентификатор пользователя.
            first_name (str): Имя пользователя.
            last_name (str): Фамилия пользователя.

        Returns:
            User: Новый активный пользователь с ролью обычного пользователя.
        """
        return User(
            user_id=UserID(user_id),
            first_name=FirstName(first_name),
            last_name=LastName(last_name),
            status=UserStatus.USER,
            state=UserState.ACTIVE,
            version=Version(1),
        )

    @staticmethod
    def restore(
        user_id: UUID,
        first_name: str,
        last_name: str,
        status: str,
        state: str,
        version: int,
    ) -> User:
        """
        Args:
            user_id (UUID): Идентификатор пользователя.
            first_name (str): Имя пользователя.
            last_name (str): Фамилия пользователя.
            status (str): Статус пользователя в строковом виде.
            state (str): Состояние пользователя в строковом виде.
            version (int): Версия агрегата.

        Returns:
            User: Восстановленная сущность пользователя.
        """
        return User(
            user_id=UserID(user_id),
            first_name=FirstName(first_name),
            last_name=LastName(last_name),
            status=UserStatus.from_str(status),
            state=UserState.from_str(state),
            version=Version(version),
        )
