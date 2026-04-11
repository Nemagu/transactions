"""Объекты значения категории транзакций."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.errors import ValueObjectInvalidDataError


@dataclass(frozen=True)
class TransactionCategoryID:
    """Объект значения идентификатора категории транзакций."""

    category_id: UUID


@dataclass(frozen=True)
class TransactionCategoryName:
    """Объект значения названия категории транзакций."""

    name: str

    def __post_init__(self) -> None:
        """
        Raises:
            ValueObjectInvalidDataError: Название категории превышает допустимый \
                лимит длины.
        """
        object.__setattr__(self, "name", self.name.strip())
        if len(self.name) > 50:
            raise ValueObjectInvalidDataError(
                msg="название категории транзакции не может содержать более 50 символов",
                struct_name="название категории транзакции",
                data={"name": self.name},
            )


@dataclass(frozen=True)
class TransactionCategoryDescription:
    """Объект значения описания категории транзакций."""

    description: str
