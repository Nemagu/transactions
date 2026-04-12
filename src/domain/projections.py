from abc import ABC
from typing import Any

from src.domain.errors import EntityIdempotentError, EntityInvalidDataError
from src.domain.value_objects import ProjectionName, State, Version


class Projection(ABC):
    def __init__(
        self,
        version: Version,
        projection_name: ProjectionName,
        id_private_field: str,
        main_error_field_name: str | None = None,
        extend_repr_fields: list[str] | None = None,
    ) -> None:
        self._version = version
        self._projection_name = projection_name
        self._str_fields = ["_version", "_projection_name"]
        if extend_repr_fields:
            self._str_fields.extend(extend_repr_fields)
        self._id_private_field = id_private_field
        self._id_error_field_name = id_private_field.replace("_", "", 1)
        if main_error_field_name:
            self._main_error_field_name = main_error_field_name
        else:
            self._main_error_field_name = id_private_field.split("_")[1]

    @property
    def version(self) -> Version:
        return self._version

    @property
    def projection_name(self) -> ProjectionName:
        return self._projection_name

    def new_version(self, version: Version) -> None:
        if self._version == version:
            raise EntityIdempotentError(
                **self._error_data(
                    "новая версия идентична текущей", {"version": version.version}
                )
            )
        if self._version.version > version.version:
            raise EntityInvalidDataError(
                **self._error_data(
                    "новая версия меньше текущей",
                    {
                        "new_version": version.version,
                        "current_version": self._version.version,
                    },
                )
            )
        self._version = version

    def _error_data(
        self, msg: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        data = data or dict()
        data[self._id_error_field_name] = str(getattr(self, self._id_error_field_name))
        return {
            "msg": msg,
            "struct_name": self._projection_name.name,
            "data": {self._main_error_field_name: data},
        }

    def __repr__(self) -> str:
        fields = ""
        for field in self._str_fields:
            if fields:
                fields = f"{fields}, {field}: {getattr(self, field)}"
            else:
                fields = f"{field}: {getattr(self, field)}"
        return f"{self.__class__.__name__}({fields})"

    def __str__(self) -> str:
        return self.__repr__()


class ProjectionWithState(Projection):
    def __init__(
        self,
        state: State,
        version: Version,
        projection_name: ProjectionName,
        id_private_field: str,
        main_error_field_name: str | None = None,
        extend_repr_fields: list[str] | None = None,
    ) -> None:
        extend_repr_fields = extend_repr_fields or list()
        extend_repr_fields.append("_state")
        super().__init__(
            version,
            projection_name,
            id_private_field,
            main_error_field_name,
            extend_repr_fields,
        )
        self._state = state

    @property
    def state(self) -> State:
        return self._state

    def new_state(self, state: State) -> None:
        if self._state == state:
            raise EntityIdempotentError(
                **self._error_data(
                    "новое состояние идентично текущему", {"state": state.value}
                )
            )
        self._state = state

    def activate(self) -> None:
        if self._state.is_active():
            raise EntityIdempotentError(
                **self._error_data(
                    f"{self._projection_name.name} уже активно",
                    {"state": self._state.value},
                )
            )
        self._state = self._state.__class__.ACTIVE

    def delete(self) -> None:
        if self._state.is_deleted():
            raise EntityIdempotentError(
                **self._error_data(
                    f"{self._projection_name.name} уже удалено",
                    {"state": self._state.value},
                )
            )
        self._state = self._state.__class__.DELETED
