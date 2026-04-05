from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID

from domain.transaction_category.errors import TransactionCategoryInvalidDataError


@dataclass(frozen=True)
class TransactionCategoryID:
    """Идентификатор категории транзакции.

    Args:
        category_id (UUID): Идентификатор.
    """

    category_id: UUID


@dataclass(frozen=True)
class TransactionCategoryName:
    """Название категории транзакции.

    Args:
        name (str): Название.

    Raises:
        TransactionCategoryInvalidDataError: Название категории ограничено 50 символами.
    """

    name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self.name.strip())
        if len(self.name) > 50:
            raise TransactionCategoryInvalidDataError(
                msg="название категории транзакции не может содержать более 50 символов",
                data={"name": self.name},
            )


@dataclass(frozen=True)
class TransactionCategoryDescription:
    """Описание категории транзакции.

    Args:
        description (str): Описание.
    """

    description: str


class TransactionCategoryState(StrEnum):
    """Состояние категории транзакции.

    Args:
        ACTIVE: Активная.
        DELETED: Удаленная.
    """

    ACTIVE = "active"
    DELETED = "deleted"

    def is_active(self) -> bool:
        """Является ли категория активной.

        Returns:
            bool: Категория активная.
        """
        return self == self.__class__.ACTIVE

    def is_deleted(self) -> bool:
        """Является ли категория удаленной.

        Returns:
            bool: Категория удалена.
        """
        return self == self.__class__.DELETED

    @classmethod
    def from_str(cls, value: str) -> Self:
        """Получение состояния категории транзакции из строки.

        Args:
            value (str): Состояние в виде строки, регистр не важен.

        Raises:
            TransactionCategoryInvalidDataError: Не удалось сопоставить строку.

        Returns:
            Self: Состояние категории транзакции.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise TransactionCategoryInvalidDataError(
            msg=(
                f"не удалось найти состояние категории транзакции по предоставленной строке - "
                f'"{value}"'
            ),
            data={"state": value},
        )
