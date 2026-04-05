from domain.errors import DomainError


class TransactionCategoryError(DomainError):
    """Базовая ошибка агрегата категорий транзакции."""


class TransactionCategoryInvalidDataError(TransactionCategoryError):
    """Некорректные данные категорий транзакции."""


class TransactionCategoryPolicyError(TransactionCategoryError):
    """Ошибка политики доступа категорий транзакции."""


class TransactionCategoryIdempotentError(TransactionCategoryError):
    """Ошибка идемпотентности категорий транзакции."""


class TransactionCategoryNotFoundError(TransactionCategoryError):
    """Категория транзакций не найдена."""
