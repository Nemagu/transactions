"""Базовые сущности и агрегаты доменного слоя."""

from abc import ABC
from typing import Any

from src.domain.errors import EntityIdempotentError, EntityInvalidDataError
from src.domain.value_objects import AggregateName, State, Version


class Entity(ABC):
    """Базовая доменная сущность с версионированием."""

    def __init__(
        self,
        version: Version,
        aggregate_name: AggregateName,
        extend_repr_fields: list[str] | None = None,
    ) -> None:
        """
        Args:
            version (Version): Текущая версия сущности.
            aggregate_name (AggregateName): Человекочитаемое имя агрегата.
            extend_repr_fields (list[str] | None): Список дополнительных полей \
                для строкового представления.
        """
        self._version = version
        self._original_version = version
        self._aggregate_name = aggregate_name
        self._str_fields = ["_version", "_aggregate_name"]
        if extend_repr_fields:
            self._str_fields.extend(extend_repr_fields)

    @property
    def version(self) -> Version:
        """
        Returns:
            Version: Текущая версия сущности.
        """
        return self._version

    @property
    def original_version(self) -> Version:
        """
        Returns:
            Version: Версия сущности на момент последней фиксации в хранилище.
        """
        return self._original_version

    @property
    def aggregate_name(self) -> AggregateName:
        """
        Returns:
            AggregateName: Имя агрегата, которому принадлежит сущность.
        """
        return self._aggregate_name

    def _update_version(self) -> None:
        """Увеличивает версию сущности при первом изменении после загрузки."""
        if self._version == self._original_version:
            self._version = Version(self._original_version.version + 1)

    def _error_data(
        self, msg: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Args:
            msg (str): Текст ошибки.
            data (dict[str, Any] | None): Дополнительные данные ошибки.

        Returns:
            dict[str, Any]: Структура данных для создания доменного исключения.
        """
        return {
            "msg": msg,
            "struct_name": self._aggregate_name.name,
            "data": data or dict(),
        }

    def mark_persisted(self) -> None:
        """Помечает текущую версию сущности как сохраненную."""
        self._original_version = self._version

    def __repr__(self) -> str:
        """
        Returns:
            str: Строковое представление сущности с основными полями.
        """
        fields = ""
        for field in self._str_fields:
            if fields:
                fields = f"{fields}, {field}: {getattr(self, field)}"
            else:
                fields = f"{field}: {getattr(self, field)}"
        return f"{self.__class__.__name__}({fields})"

    def __str__(self) -> str:
        """
        Returns:
            str: Человекочитаемое строковое представление сущности.
        """
        return self.__repr__()


class EntityWithState(Entity):
    """Базовая сущность, поддерживающая состояние активности и удаления."""

    def __init__(
        self,
        state: State,
        version: Version,
        aggregate_name: AggregateName,
        extend_repr_fields: list[str] | None = None,
    ) -> None:
        """
        Args:
            state (State): Начальное состояние сущности.
            version (Version): Текущая версия сущности.
            aggregate_name (AggregateName): Имя агрегата.
            extend_repr_fields (list[str] | None): Дополнительные поля для \
                строкового представления.
        """
        extend_repr_fields = extend_repr_fields or list()
        extend_repr_fields.append("_state")
        super().__init__(version, aggregate_name, extend_repr_fields)
        self._state = state

    @property
    def state(self) -> State:
        """
        Returns:
            State: Текущее состояние сущности.
        """
        return self._state

    def new_state(self, state: State) -> None:
        """
        Args:
            state (State): Новое состояние сущности.

        Raises:
            EntityIdempotentError: Передано состояние, совпадающее с текущим.
        """
        if self._state == state:
            raise EntityIdempotentError(
                **self._error_data(
                    "новое состояние идентично текущему", {"state": state.value}
                )
            )
        self._state = state
        self._update_version()

    def activate(self) -> None:
        """
        Raises:
            EntityIdempotentError: Сущность уже находится в активном состоянии.
        """
        if self._state.is_active():
            raise EntityIdempotentError(
                **self._error_data(
                    f"{self._aggregate_name.name}. уже активно",
                    {"state": self._state.value},
                )
            )
        self._state = self._state.__class__.ACTIVE
        self._update_version()

    def delete(self) -> None:
        """
        Raises:
            EntityIdempotentError: Сущность уже находится в удаленном состоянии.
        """
        if self._state.is_deleted():
            raise EntityIdempotentError(
                **self._error_data(
                    f"{self._aggregate_name.name}. уже удалено",
                    {"state": self._state.value},
                )
            )
        self._state = self._state.__class__.DELETED
        self._update_version()

    def _check_state(self, msg: str, data: dict[str, Any] | None = None) -> None:
        """
        Args:
            msg (str): Сообщение об ошибке для удаленной сущности.
            data (dict[str, Any] | None): Дополнительные диагностические данные.

        Raises:
            EntityInvalidDataError: Сущность находится в удаленном состоянии.
        """
        data = data or dict()
        data["state"] = self._state.value
        if self._state.is_deleted():
            raise EntityInvalidDataError(**self._error_data(msg, data))
