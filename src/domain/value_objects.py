"""Общие объекты значения, используемые доменным слоем."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from src.domain.errors import ValueObjectInvalidDataError


@dataclass(frozen=True)
class Version:
    """Объект значения версии агрегата."""

    version: int

    def __post_init__(self) -> None:
        """
        Raises:
            ValueObjectInvalidDataError: Передана версия меньше единицы.
        """
        if self.version < 1:
            raise ValueObjectInvalidDataError(
                msg="версия не может быть меньше 1",
                struct_name="версия агрегата",
                data={"version": self.version},
            )


@dataclass(frozen=True)
class AggregateName:
    """Объект значения имени агрегата."""

    name: str

    def __post_init__(self) -> None:
        """
        Raises:
            ValueObjectInvalidDataError: Название агрегата пустое или слишком длинное.
        """
        object.__setattr__(self, "name", self.name.strip())
        name_len = len(self.name)
        if name_len == 0:
            raise ValueObjectInvalidDataError(
                msg="название агрегата не может быть пустым",
                struct_name="название агрегата",
                data={"aggregate_name": self.name},
            )
        if name_len > 50:
            raise ValueObjectInvalidDataError(
                msg="название агрегата не может содержать более 50 символов",
                struct_name="название агрегата",
                data={"aggregate_name": self.name},
            )


class State(StrEnum):
    """Базовое состояние агрегата с поддержкой мягкого удаления."""

    ACTIVE = "active"
    DELETED = "deleted"

    def is_active(self) -> bool:
        """
        Returns:
            bool: `True`, если состояние активно.
        """
        return self == self.__class__.ACTIVE

    def is_deleted(self) -> bool:
        """
        Returns:
            bool: `True`, если состояние соответствует удалению.
        """
        return self == self.__class__.DELETED

    @classmethod
    def from_str(cls, value: str) -> Self:
        """
        Args:
            value (str): Строковое представление состояния.

        Raises:
            ValueObjectInvalidDataError: Передана строка, которой нет в перечислении.

        Returns:
            Self: Найденное состояние.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise ValueObjectInvalidDataError(
            msg="не удалось найти состояние по предоставленной строке",
            struct_name="состояние агрегата",
            data={"state": value},
        )
