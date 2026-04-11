"""Доменная сущность пользователя."""

from src.domain.entities import Entity
from src.domain.errors import (
    EntityIdempotentError,
    EntityInvalidDataError,
    EntityPolicyError,
)
from src.domain.user.value_objects import (
    FirstName,
    LastName,
    UserID,
    UserState,
    UserStatus,
)
from src.domain.value_objects import AggregateName, Version


class User(Entity):
    """Сущность пользователя системы."""

    def __init__(
        self,
        user_id: UserID,
        first_name: FirstName,
        last_name: LastName,
        status: UserStatus,
        state: UserState,
        version: Version,
    ):
        """
        Args:
            user_id (UserID): Идентификатор пользователя.
            first_name (FirstName): Имя пользователя.
            last_name (LastName): Фамилия пользователя.
            status (UserStatus): Текущий статус пользователя.
            state (UserState): Текущее состояние пользователя.
            version (Version): Версия агрегата.
        """
        super().__init__(
            version,
            AggregateName("пользователь"),
            ["_user_id", "_first_name", "_last_name", "_status", "_state"],
        )
        self._user_id = user_id
        self._first_name = first_name
        self._last_name = last_name
        self._status = status
        self._state = state

    @property
    def user_id(self) -> UserID:
        """
        Returns:
            UserID: Идентификатор пользователя.
        """
        return self._user_id

    @property
    def first_name(self) -> FirstName:
        """
        Returns:
            FirstName: Текущее имя пользователя.
        """
        return self._first_name

    @property
    def last_name(self) -> LastName:
        """
        Returns:
            LastName: Текущая фамилия пользователя.
        """
        return self._last_name

    @property
    def status(self) -> UserStatus:
        """
        Returns:
            UserStatus: Текущий статус пользователя.
        """
        return self._status

    @property
    def state(self) -> UserState:
        """
        Returns:
            UserState: Текущее состояние пользователя.
        """
        return self._state

    def raise_staff(self) -> None:
        """
        Raises:
            EntityPolicyError: Пользователь не является администратором, удален \
                или заморожен.
        """
        if self._state.is_deleted():
            raise EntityPolicyError(
                **self._error_data(
                    "вы удалены",
                    {"user_id": str(self._user_id.user_id), "state": self._state.value},
                )
            )
        if self._state.is_frozen():
            raise EntityPolicyError(
                **self._error_data(
                    "вы заморожены",
                    {"user_id": str(self._user_id.user_id), "state": self._state.value},
                )
            )
        if not self._status.is_admin():
            raise EntityPolicyError(
                **self._error_data(
                    "вы не являетесь администратором",
                    {"user_id": str(self._user_id.user_id), "state": self._state.value},
                )
            )

    def new_first_name(self, first_name: FirstName) -> None:
        """
        Args:
            first_name (FirstName): Новое имя пользователя.

        Raises:
            EntityIdempotentError: Передано имя, совпадающее с текущим.
        """
        self._check_state()
        if self._first_name == first_name:
            raise EntityIdempotentError(
                **self._error_data(
                    "имя пользователя идентично текущему имени",
                    {
                        "user_id": str(self._user_id.user_id),
                        "first_name": first_name.first_name,
                    },
                )
            )
        self._first_name = first_name
        self._update_version()

    def new_last_name(self, last_name: LastName) -> None:
        """
        Args:
            last_name (LastName): Новая фамилия пользователя.

        Raises:
            EntityIdempotentError: Передана фамилия, совпадающая с текущей.
        """
        self._check_state()
        if self._last_name == last_name:
            raise EntityIdempotentError(
                **self._error_data(
                    "фамилия пользователя идентична текущей фамилии",
                    {
                        "user_id": str(self._user_id.user_id),
                        "last_name": last_name.last_name,
                    },
                )
            )
        self._last_name = last_name
        self._update_version()

    def appoint_admin(self) -> None:
        """
        Raises:
            EntityIdempotentError: Пользователь уже имеет статус администратора.
        """
        self._check_state()
        if self._status.is_admin():
            raise EntityIdempotentError(
                **self._error_data(
                    "пользователь уже является администратором",
                    {
                        "user_id": str(self._user_id.user_id),
                        "status": self._status.value,
                    },
                )
            )
        self._status = UserStatus.ADMIN
        self._update_version()

    def appoint_user(self) -> None:
        """
        Raises:
            EntityIdempotentError: Пользователь уже имеет статус обычного \
                пользователя.
        """
        self._check_state()
        if self._status.is_user():
            raise EntityIdempotentError(
                **self._error_data(
                    "пользователь уже является пользователем",
                    {
                        "user_id": str(self._user_id.user_id),
                        "status": self._status.value,
                    },
                )
            )
        self._status = UserStatus.USER
        self._update_version()

    def activate(self) -> None:
        """
        Raises:
            EntityIdempotentError: Пользователь уже активен.
        """
        if self._state.is_active():
            raise EntityIdempotentError(
                **self._error_data(
                    "пользователь уже является активным",
                    {"user_id": str(self._user_id.user_id), "state": self._state.value},
                )
            )
        self._state = UserState.ACTIVE
        self._update_version()

    def freeze(self) -> None:
        """
        Raises:
            EntityIdempotentError: Пользователь уже заморожен.
        """
        if self._state.is_frozen():
            raise EntityIdempotentError(
                **self._error_data(
                    "пользователь уже является замороженным",
                    {"user_id": str(self._user_id.user_id), "state": self._state.value},
                )
            )
        self._state = UserState.FROZEN
        self._update_version()

    def delete(self) -> None:
        """
        Raises:
            EntityIdempotentError: Пользователь уже удален.
        """
        if self._state.is_deleted():
            raise EntityIdempotentError(
                **self._error_data(
                    "пользователь уже является удаленным",
                    {"user_id": str(self._user_id.user_id), "state": self._state.value},
                )
            )
        self._state = UserState.DELETED
        self._update_version()

    def _check_state(self) -> None:
        """
        Raises:
            EntityInvalidDataError: Пользователь удален или заморожен.
        """
        if self._state.is_deleted():
            raise EntityInvalidDataError(
                **self._error_data(
                    "пользователь удален",
                    {"user_id": str(self._user_id.user_id), "state": self._state.value},
                )
            )
        if self._state.is_frozen():
            raise EntityInvalidDataError(
                **self._error_data(
                    "пользователь заморожен",
                    {"user_id": str(self._user_id.user_id), "state": self._state.value},
                )
            )
