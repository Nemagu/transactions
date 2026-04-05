from typing import Any


class DomainError(Exception):
    """Базовая доменная ошибка."""

    def __init__(
        self,
        msg: str,
        data: dict[str, Any] | None = None,
        *args: object,
    ) -> None:
        """
        Args:
            msg (str): Сообщение ошибки.
            data (dict[str, Any], optional): Детализация ошибки. По умолчанию пустой словарь.
        """
        super().__init__(msg, *args)
        self.msg = msg
        self.data = data or {}


class VersionError(DomainError):
    """Ошибка версии агрегата."""
