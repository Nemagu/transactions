from uuid import UUID

from domain.user.entity import User
from domain.user.value_objects import FirstName, LastName, UserID, UserState, UserStatus
from domain.value_objects import Version


class UserFactory:
    """Фабрика создания и восстановления пользователя."""

    @staticmethod
    def new(user_id: UUID, first_name: str = "", last_name: str = "") -> User:
        """Создание нового пользователя.

        Args:
            user_id (UUID): Идентификатор для нового пользователя.
            first_name (str, optional): Имя нового пользователя. По умолчанию пустая \
                строка.
            last_name (str, optional): Фамилия нового пользователя. По умолчанию пустая \
                строка.

        Raises:
            UserDomainError: Ошибки при создании объектов значений из переданных данных.

        Returns:
            User: Новый пользователь.
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
        """Восстановление пользователя.

        Args:
            user_id (UUID): Идентификатор пользователя.
            first_name (str): Имя пользователя.
            last_name (str): Фамилия пользователя.
            status (str): Статус пользователя.
            state (str): Состояние пользователя.
            version (int): Версия пользователя.

        Raises:
            UserDomainError: Ошибки при создании объектов значений из переданных данных.

        Returns:
            User: Восстановленный пользователь.
        """
        return User(
            user_id=UserID(user_id),
            first_name=FirstName(first_name),
            last_name=LastName(last_name),
            status=UserStatus.from_str(status),
            state=UserState.from_str(state),
            version=Version(version),
        )
