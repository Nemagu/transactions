from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self
from uuid import UUID

from domain.personal_transaction.errors import PersonalTransactionInvalidDataError


@dataclass(frozen=True)
class PersonalTransactionID:
    """Идентификатор персональной транзакции.

    Args:
        transaction_id (UUID): Идентификатор.
    """

    transaction_id: UUID


@dataclass(frozen=True)
class PersonalTransactionName:
    """Название персональной транзакции.

    Args:
        name (str): Название.

    Raises:
        PersonalTransactionInvalidDataError: Название транзакции ограничено 50
            символами.
    """

    name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self.name.strip())
        if len(self.name) > 50:
            raise PersonalTransactionInvalidDataError(
                msg="название транзакции не может содержать более 100 символов",
                data={"name": self.name},
            )


@dataclass(frozen=True)
class PersonalTransactionDescription:
    """Описание персональной транзакции.

    Args:
        description (str): Описание.
    """

    description: str


class PersonalTransactionType(StrEnum):
    """Тип персональной транзакции.

    Args:
        EXPENSE: Расход.
        INCOME: Доход.
    """

    EXPENSE = "expense"
    INCOME = "income"

    def is_expense(self) -> bool:
        """Является ли транзакция расходом.

        Returns:
            bool: Транзакция является расходом.
        """
        return self == self.__class__.EXPENSE

    def is_income(self) -> bool:
        """Является ли транзакция доходом.

        Returns:
            bool: Транзакция является доходом.
        """
        return self == self.__class__.INCOME

    @classmethod
    def from_str(cls, value: str) -> Self:
        """Получение типа транзакции из строки.

        Args:
            value (str): Тип в виде строки, регистр не важен.

        Raises:
            PersonalTransactionInvalidDataError: Не удалось сопоставить строку.

        Returns:
            Self: Тип персональной транзакции.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise PersonalTransactionInvalidDataError(
            msg=(
                f'не удалось найти тип транзакции по предоставленной строке - "{value}"'
            ),
            data={"transaction_type": value},
        )


class Currency(StrEnum):
    """Валюта персональной транзакции.

    Args:
        RUBLE: Российский рубль.
        DOLLAR: Доллар США.
        EURO: Евро.
        YUAN: Китайский юань.
    """

    RUBLE = "ruble"
    DOLLAR = "dollar"
    EURO = "euro"
    YUAN = "yuan"

    @classmethod
    def from_str(cls, value: str) -> Self:
        """Получение валюты из строки.

        Args:
            value (str): Валюта в виде строки, регистр не важен.

        Raises:
            PersonalTransactionInvalidDataError: Не удалось сопоставить строку.

        Returns:
            Self: Валюта персональной транзакции.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise PersonalTransactionInvalidDataError(
            msg=(f'не удалось найти валюту по предоставленной строке - "{value}"'),
            data={"currency": value},
        )


@dataclass(frozen=True)
class MoneyAmount:
    """Количество средств персональной транзакции.

    Args:
        amount (Decimal): Количество средств.
        currency (Currency): Валюта.

    Raises:
        PersonalTransactionInvalidDataError: Количество средств должно быть больше
            нуля.
    """

    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise PersonalTransactionInvalidDataError(
                msg="количество средств не может быть равна 0 и менее",
                data={
                    "money_amount": {
                        "amount": str(self.amount),
                        "currency": self.currency.value,
                    }
                },
            )


@dataclass(frozen=True)
class PersonalTransactionTime:
    """Время персональной транзакции.

    Args:
        transaction_time (datetime): Время транзакции.
    """

    transaction_time: datetime


class PersonalTransactionState(StrEnum):
    """Состояние персональной транзакции.

    Args:
        ACTIVE: Активная.
        DELETED: Удаленная.
    """

    ACTIVE = "active"
    DELETED = "deleted"

    def is_active(self) -> bool:
        """Является ли транзакция активной.

        Returns:
            bool: Транзакция активная.
        """
        return self == self.__class__.ACTIVE

    def is_deleted(self) -> bool:
        """Является ли транзакция удаленной.

        Returns:
            bool: Транзакция удалена.
        """
        return self == self.__class__.DELETED

    @classmethod
    def from_str(cls, value: str) -> Self:
        """Получение состояния транзакции из строки.

        Args:
            value (str): Состояние в виде строки, регистр не важен.

        Raises:
            PersonalTransactionInvalidDataError: Не удалось сопоставить строку.

        Returns:
            Self: Состояние персональной транзакции.
        """
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise PersonalTransactionInvalidDataError(
            msg=(
                f'не удалось найти состояние транзакции по предоставленной строке - "{value}"'
            ),
            data={"state": value},
        )
