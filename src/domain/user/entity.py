from domain.entities import Entity
from domain.user.errors import UserIdempotentError
from domain.user.value_objects import FirstName, LastName, UserID, UserState, UserStatus
from domain.value_objects import Version


class User(Entity):
    """Агрегат пользователя."""

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
            status (UserStatus): Статус пользователя.
            state (UserState): Состояние пользователя.
            version (Version): Версия пользователя.
        """
        super().__init__(version)
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
            FirstName: Имя пользователя.
        """
        return self._first_name

    @property
    def last_name(self) -> LastName:
        """
        Returns:
            LastName: Фамилия пользователя.
        """
        return self._last_name

    @property
    def status(self) -> UserStatus:
        """
        Returns:
            UserStatus: Статус пользователя.
        """
        return self._status

    @property
    def state(self) -> UserState:
        """
        Returns:
            UserState: Состояние пользователя.
        """
        return self._state

    def new_first_name(self, first_name: FirstName) -> None:
        """Смена имени пользователя.

        Args:
            first_name (FirstName): Новое имя пользователя.

        Raises:
            UserIdempotentError: Новое имя пользователя не может совпадать с \
                предыдущим.
        """
        if self._first_name == first_name:
            raise UserIdempotentError(
                msg="имя пользователя идентично текущему имени",
                data={"first_name": first_name.first_name},
            )
        self._first_name = first_name
        self._update_version()

    def new_last_name(self, last_name: LastName) -> None:
        """Смена фамилии пользователя.

        Args:
            last_name (LastName): Новая фамилия пользователя.

        Raises:
            UserIdempotentError: Новая фамилия пользователя не может совпадать с \
                предыдущей.
        """
        if self._last_name == last_name:
            raise UserIdempotentError(
                msg="фамилия пользователя идентично текущему имени",
                data={"last_name": last_name.last_name},
            )
        self._last_name = last_name
        self._update_version()

    def appoint_admin(self) -> None:
        """Назначить пользователя администратором.

        Raises:
            UserIdempotentError: Администратора нельзя повторно назначить \
                администратором.
        """
        if self._status.is_admin():
            raise UserIdempotentError(
                msg="пользователь уже является администратором",
                data={"status": self._status.value},
            )
        self._status = UserStatus.ADMIN
        self._update_version()

    def appoint_user(self) -> None:
        """Назначить пользователя обычным пользователем.

        Raises:
            UserIdempotentError: Обычного пользователя нельзя повторно назначить \
                обычным пользователем.
        """
        if self._status.is_user():
            raise UserIdempotentError(
                msg="пользователь уже является пользователем",
                data={"status": self._status.value},
            )
        self._status = UserStatus.USER
        self._update_version()

    def activate(self) -> None:
        """Активировать пользователя.

        Raises:
            UserIdempotentError: Активного пользователя нельзя повторно активировать.
        """
        if self._state.is_active():
            raise UserIdempotentError(
                msg="пользователь уже является активным",
                data={"state": self._state.value},
            )
        self._state = UserState.ACTIVE
        self._update_version()

    def freeze(self) -> None:
        """Заморозить пользователя.

        Raises:
            UserIdempotentError: Замороженного пользователя нельзя повторно заморозить.
        """
        if self._state.is_frozen():
            raise UserIdempotentError(
                msg="пользователь уже является замороженным",
                data={"state": self._state.value},
            )
        self._state = UserState.FROZEN
        self._update_version()

    def delete(self) -> None:
        """Удалить пользователя.

        Raises:
            UserIdempotentError: Удаленного пользователя нельзя повторно удалить.
        """
        if self._state.is_deleted():
            raise UserIdempotentError(
                msg="пользователь уже является удаленным",
                data={"state": self._state.value},
            )
        self._state = UserState.DELETED
        self._update_version()
