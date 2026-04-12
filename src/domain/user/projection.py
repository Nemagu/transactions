from domain.errors import EntityIdempotentError
from domain.projections import Projection
from domain.user.value_objects import UserID, UserState
from domain.value_objects import ProjectionName, Version


class User(Projection):
    def __init__(
        self,
        user_id: UserID,
        state: UserState,
        version: Version,
    ) -> None:
        super().__init__(
            version,
            ProjectionName("проекция пользователя"),
            "_user_id",
            "user",
            ["_user_id", "_state"],
        )
        self._user_id = user_id
        self._state = state

    @property
    def user_id(self) -> UserID:
        return self._user_id

    @property
    def state(self) -> UserState:
        return self._state

    def new_state(self, state: UserState) -> None:
        if self._state == state:
            raise EntityIdempotentError(
                **self._error_data(
                    "новое состояние пользователя идентично текущему",
                    {"state": self._state.value},
                )
            )
        self._state = state
