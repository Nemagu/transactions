from dataclasses import dataclass
from uuid import UUID

from domain.errors import ValueObjectInvalidDataError


@dataclass(frozen=True)
class TransactionCategoryID:
    category_id: UUID


@dataclass(frozen=True)
class TransactionCategoryName:
    name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self.name.strip())
        struct_name = "название категории транзакции"
        data = {"name": self.name}
        if len(self.name) > 50:
            raise ValueObjectInvalidDataError(
                msg="название категории транзакции не может содержать более 50 символов",
                struct_name=struct_name,
                data=data,
            )
        if len(self.name) == 0:
            raise ValueObjectInvalidDataError(
                msg="название категории транзакции не может быть пустым",
                struct_name=struct_name,
                data=data,
            )


@dataclass(frozen=True)
class TransactionCategoryDescription:
    description: str
