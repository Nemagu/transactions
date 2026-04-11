"""Общие исключения доменного слоя."""

from typing import Any


class DomainError(Exception):
    """Базовое исключение доменного слоя.

    Args:
        msg (str): Человекочитаемое описание причины ошибки.
        struct_name (str): Имя доменной структуры, в которой произошла ошибка.
        data (dict[str, Any] | None): Дополнительные диагностические данные.
        *args (object): Дополнительные аргументы базового класса `Exception`.
    """

    def __init__(
        self,
        msg: str,
        struct_name: str,
        data: dict[str, Any] | None = None,
        *args: object,
    ) -> None:
        """
        Args:
            msg (str): Человекочитаемое описание причины ошибки.
            struct_name (str): Имя доменной структуры, в которой произошла ошибка.
            data (dict[str, Any] | None): Дополнительные диагностические данные.
            *args (object): Дополнительные аргументы базового класса `Exception`.
        """
        super().__init__(msg, *args)
        self.msg = msg
        self.struct_name = struct_name
        self.data = data or {}


class ValueObjectInvalidDataError(DomainError):
    """Исключение, возникающее при создании value object с некорректными данными."""


class EntityInvalidDataError(DomainError):
    """Исключение, возникающее при нарушении инвариантов сущности."""


class EntityIdempotentError(DomainError):
    """Исключение, возникающее при повторном выполнении уже примененного действия."""


class EntityPolicyError(DomainError):
    """Исключение, возникающее при нарушении доменных правил доступа."""
