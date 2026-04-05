from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID

from domain.user.errors import UserInvalidDataError


@dataclass(frozen=True)
class UserID:
    """Идентификатор пользователя.

    Args:
        user_id (UUID): Идентификатор.
    """

    user_id: UUID


@dataclass(frozen=True)
class FirstName:
    """Имя пользователя.

    Args:
        first_name (str): Имя.

    Raises:
        UserInvalidDataError: Имя пользователя ограничено 50 символами.
    """

    first_name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "first_name", self.first_name.strip())
        if len(self.first_name) > 50:
            raise UserInvalidDataError(
                msg="имя пользователя не может содержать более 50 символов",
                data={"first_name": self.first_name},
            )


@dataclass(frozen=True)
class LastName:
    """Фамилия пользователя.

    Args:
        last_name (str): Фамилия.

    Raises:
        UserInvalidDataError: Фамилия пользователя ограничена 50 символами.
    """

    last_name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "last_name", self.last_name.strip())
        if len(self.last_name) > 50:
            raise UserInvalidDataError(
                msg="фамилия пользователя не может содержать более 50 символов",
                data={"last_name": self.last_name},
            )


class UserStatus(StrEnum):
    """Статус пользователя.

    Args:
        ADMIN: Администратор.
        USER: Обычный пользователь.
    """

    ADMIN = "admin"
    USER = "user"

    def is_admin(self) -> bool:
        """Является ли пользователь администратором.

        Returns:
            bool: Пользователь администратор.
        """
        return self == self.__class__.ADMIN

    def is_user(self) -> bool:
        """Является ли пользователь обычным пользователем.

        Returns:
            bool: Пользователь обычный.
        """
        return self == self.__class__.USER

    @classmethod
    def from_str(cls, value: str) -> Self:
        """Получение статуса пользователя из строки.

        Args:
            value (str): Статус в виде строки, регистр не важен.

        Raises:
            UserInvalidDataError: Не удалось сопоставить строку.

        Returns:
            Self: Статус пользователя.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise UserInvalidDataError(
            msg=(
                f"не удалось найти статус пользователя по предоставленной строке - "
                f'"{value}"'
            ),
            data={"status": value},
        )


class UserState(StrEnum):
    """Состояние пользователя.

    Args:
        ACTIVE: Активный.
        FROZEN: Замороженный.
        DELETED: Удаленный.
    """

    ACTIVE = "active"
    FROZEN = "frozen"
    DELETED = "deleted"

    def is_active(self) -> bool:
        """Является ли пользователь активным.

        Returns:
            bool: Пользователь активный.
        """
        return self == self.__class__.ACTIVE

    def is_frozen(self) -> bool:
        """Является ли пользователь замороженным.

        Returns:
            bool: Пользователь заморожен.
        """
        return self == self.__class__.FROZEN

    def is_deleted(self) -> bool:
        """Является ли пользователь удаленным.

        Returns:
            bool: Пользователь удален.
        """
        return self == self.__class__.DELETED

    @classmethod
    def from_str(cls, value: str) -> Self:
        """Получение состояния пользователя из строки.

        Args:
            value (str): Состояние в виде строки, регистр не важен.

        Raises:
            UserInvalidDataError: Не удалось сопоставить строку.

        Returns:
            Self: Состояние пользователя.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise UserInvalidDataError(
            msg=(
                f"не удалось найти состояние пользователя по предоставленной строке - "
                f'"{value}"'
            ),
            data={"state": value},
        )
