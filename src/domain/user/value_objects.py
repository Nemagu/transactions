"""Объекты значения пользователя."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID

from src.domain.errors import ValueObjectInvalidDataError


@dataclass(frozen=True)
class UserID:
    """Объект значения идентификатора пользователя."""

    user_id: UUID


@dataclass(frozen=True)
class FirstName:
    """Объект значения имени пользователя."""

    first_name: str

    def __post_init__(self) -> None:
        """
        Raises:
            ValueObjectInvalidDataError: Имя пользователя длиннее допустимого лимита.
        """
        object.__setattr__(self, "first_name", self.first_name.strip())
        if len(self.first_name) > 50:
            raise ValueObjectInvalidDataError(
                msg="имя пользователя не может содержать более 50 символов",
                struct_name="имя пользователя",
                data={"first_name": self.first_name},
            )


@dataclass(frozen=True)
class LastName:
    """Объект значения фамилии пользователя."""

    last_name: str

    def __post_init__(self) -> None:
        """
        Raises:
            ValueObjectInvalidDataError: Фамилия пользователя длиннее допустимого \
                лимита.
        """
        object.__setattr__(self, "last_name", self.last_name.strip())
        if len(self.last_name) > 50:
            raise ValueObjectInvalidDataError(
                msg="фамилия пользователя не может содержать более 50 символов",
                struct_name="фамилия пользователя",
                data={"last_name": self.last_name},
            )


class UserStatus(StrEnum):
    """Доступные статусы пользователя в системе."""

    ADMIN = "admin"
    USER = "user"

    def is_admin(self) -> bool:
        """
        Returns:
            bool: `True`, если пользователь является администратором.
        """
        return self == self.__class__.ADMIN

    def is_user(self) -> bool:
        """
        Returns:
            bool: `True`, если пользователь является обычным пользователем.
        """
        return self == self.__class__.USER

    @classmethod
    def from_str(cls, value: str) -> Self:
        """
        Args:
            value (str): Строковое представление статуса пользователя.

        Raises:
            ValueObjectInvalidDataError: Передано неизвестное строковое значение.

        Returns:
            Self: Найденный статус пользователя.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise ValueObjectInvalidDataError(
            msg=(
                f"не удалось найти статус пользователя по предоставленной строке - "
                f'"{value}"'
            ),
            struct_name="статус пользователя",
            data={"status": value},
        )


class UserState(StrEnum):
    """Состояния жизненного цикла пользователя."""

    ACTIVE = "active"
    FROZEN = "frozen"
    DELETED = "deleted"

    def is_active(self) -> bool:
        """
        Returns:
            bool: `True`, если пользователь активен.
        """
        return self == self.__class__.ACTIVE

    def is_frozen(self) -> bool:
        """
        Returns:
            bool: `True`, если пользователь заморожен.
        """
        return self == self.__class__.FROZEN

    def is_deleted(self) -> bool:
        """
        Returns:
            bool: `True`, если пользователь удален.
        """
        return self == self.__class__.DELETED

    @classmethod
    def from_str(cls, value: str) -> Self:
        """
        Args:
            value (str): Строковое представление состояния пользователя.

        Raises:
            ValueObjectInvalidDataError: Передано неизвестное строковое значение.

        Returns:
            Self: Найденное состояние пользователя.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise ValueObjectInvalidDataError(
            msg=(
                f"не удалось найти состояние пользователя по предоставленной строке - "
                f'"{value}"'
            ),
            struct_name="состояние пользователя",
            data={"state": value},
        )
