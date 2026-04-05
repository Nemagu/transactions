from domain.errors import DomainError


class PersonalTransactionError(DomainError):
    """Базовая ошибка агрегата персональной транзакции."""


class PersonalTransactionInvalidDataError(PersonalTransactionError):
    """Некорректные данные персональной транзакции."""


class PersonalTransactionPolicyError(PersonalTransactionError):
    """Ошибка политики доступа персональной транзакции."""


class PersonalTransactionIdempotentError(PersonalTransactionError):
    """Ошибка идемпотентности персональной транзакции."""


class PersonalTransactionNotFoundError(PersonalTransactionError):
    """Персональной транзакций не найдено."""
