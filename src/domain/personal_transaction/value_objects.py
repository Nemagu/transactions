from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self
from uuid import UUID

from src.domain.errors import ValueObjectInvalidDataError


@dataclass(frozen=True)
class PersonalTransactionID:
    transaction_id: UUID


@dataclass(frozen=True)
class PersonalTransactionName:
    name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self.name.strip())
        if len(self.name) > 100:
            raise ValueObjectInvalidDataError(
                msg="название транзакции не может содержать более 100 символов",
                struct_name="название персональной транзакции",
                data={"name": self.name},
            )


@dataclass(frozen=True)
class PersonalTransactionDescription:
    description: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "description", self.description.strip())


class PersonalTransactionType(StrEnum):
    EXPENSE = "expense"
    INCOME = "income"

    def is_expense(self) -> bool:
        return self == self.__class__.EXPENSE

    def is_income(self) -> bool:
        return self == self.__class__.INCOME

    @classmethod
    def from_str(cls, value: str) -> Self:
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise ValueObjectInvalidDataError(
            msg=(
                f'не удалось найти тип транзакции по предоставленной строке - "{value}"'
            ),
            struct_name="тип персональной транзакции",
            data={"transaction_type": value},
        )


class Currency(StrEnum):
    RUBLE = "ruble"
    DOLLAR = "dollar"
    EURO = "euro"
    YUAN = "yuan"

    @classmethod
    def from_str(cls, value: str) -> Self:
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise ValueObjectInvalidDataError(
            msg=(f'не удалось найти валюту по предоставленной строке - "{value}"'),
            struct_name="валюта",
            data={"currency": value},
        )


@dataclass(frozen=True)
class MoneyAmount:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueObjectInvalidDataError(
                msg="количество средств не может быть менее 0",
                struct_name="количество средств",
                data={
                    "money_amount": {
                        "amount": str(self.amount),
                        "currency": self.currency.value,
                    }
                },
            )


@dataclass(frozen=True)
class PersonalTransactionTime:
    transaction_time: datetime
