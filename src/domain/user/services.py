from domain.user.entity import User
from domain.user.errors import UserNotFoundError, UserPolicyError
from domain.user.repository import UserRepository
from domain.user.value_objects import UserID


class UserPolicyService:
    """Сервис проверки прав доступа для работы с пользователями."""

    @staticmethod
    def is_staff(user: User) -> None:
        """Является пользователь администратором.

        Args:
            user (User): Пользователь, которого нужно проверить.

        Raises:
            UserPolicyError: Пользователь не является администратором.
        """
        if user.status.is_user():
            raise UserPolicyError(
                msg="у вас недостаточно прав для редактирования",
                data={"status": user.status.value},
            )
        if user.state.is_frozen():
            raise UserPolicyError(
                msg=("вы администратор, но заморожены другим администратором"),
                data={"state": user.state.value},
            )
        if user.state.is_deleted():
            raise UserPolicyError(
                msg=("вы администратор, но вы удалены"),
                data={"state": user.state.value},
            )

    @staticmethod
    def can_edit_user(user: User) -> None:
        """Можно ли редактировать переданного пользователя.

        Args:
            user (User): Пользователь, которого нужно проверить.

        Raises:
            UserPolicyError: Редактирование пользователя запрещено.
        """
        if user.state.is_frozen():
            raise UserPolicyError(
                msg="пользователь заморожен администратором",
                data={"state": user.state.value},
            )
        if user.state.is_deleted():
            raise UserPolicyError(
                msg="пользователь удален",
                data={"state": user.state.value},
            )


class UserEditorStatusService:
    """Сервис редактирования статуса пользователей."""

    def __init__(self, repository: UserRepository) -> None:
        """
        Args:
            repository (UserRepository): Репозиторий пользователей.
        """
        self._repo = repository

    async def appoint_admin(self, initiator_user_id: UserID, user_id: UserID) -> None:
        """Назначение пользователя администратором.

        Args:
            initiator_user_id (UserID): Идентификатор пользователя-инициатора.
            user_id (UserID): Идентификатор назначаемого пользователя.

        Raises:
            UserNotFoundError: Инициатор или назначаемый пользователь не найдены.
        """
        initiator = await self._get_user("инициатор не найден", initiator_user_id)
        UserPolicyService.is_staff(initiator)
        if initiator_user_id == user_id:
            target = initiator
        else:
            target = await self._get_user("пользователь не найден", user_id)
        UserPolicyService.can_edit_user(target)
        target.appoint_admin()
        await self._repo.save(target)

    async def appoint_user(self, initiator_user_id: UserID, user_id: UserID) -> None:
        """Назначение пользователя обычным пользователем.

        Args:
            initiator_user_id (UserID): Идентификатор пользователя-инициатора.
            user_id (UserID): Идентификатор назначаемого пользователя.

        Raises:
            UserNotFoundError: Инициатор или назначаемый пользователь не найдены.
        """
        initiator = await self._get_user("инициатор не найден", initiator_user_id)
        UserPolicyService.is_staff(initiator)
        if initiator_user_id == user_id:
            target = initiator
        else:
            target = await self._get_user("пользователь не найден", user_id)
        UserPolicyService.can_edit_user(target)
        target.appoint_user()
        await self._repo.save(target)

    async def _get_user(self, error_msg: str, user_id: UserID) -> User:
        user = await self._repo.by_id(user_id)
        if user is None:
            raise UserNotFoundError(msg=error_msg, data={"user_id": user_id.user_id})
        return user


class UserEditorStateService:
    """Сервис редактирования состояния пользователей."""

    def __init__(self, repository: UserRepository) -> None:
        """
        Args:
            repository (UserRepository): Репозиторий пользователей.
        """
        self._repo = repository

    async def activate(self, initiator_user_id: UserID, user_id: UserID) -> None:
        """Активация пользователя.

        Args:
            initiator_user_id (UserID): Идентификатор пользователя-инициатора.
            user_id (UserID): Идентификатор активируемого пользователя.

        Raises:
            UserNotFoundError: Инициатор или активируемый пользователь не найдены.
        """
        initiator = await self._get_user("инициатор не найден", initiator_user_id)
        if initiator_user_id == user_id:
            if initiator.state.is_frozen():
                UserPolicyService.is_staff(initiator)
            target = initiator
        else:
            UserPolicyService.is_staff(initiator)
            target = await self._get_user("пользователь не найден", user_id)
        target.activate()
        await self._repo.save(target)

    async def freeze(self, initiator_user_id: UserID, user_id: UserID) -> None:
        """Заморозка пользователя.

        Args:
            initiator_user_id (UserID): Идентификатор пользователя-инициатора.
            user_id (UserID): Идентификатор замораживаемого пользователя.

        Raises:
            UserNotFoundError: Инициатор или замораживаемый пользователь не найдены.
        """
        initiator = await self._get_user("инициатор не найден", initiator_user_id)
        UserPolicyService.is_staff(initiator)
        if initiator_user_id == user_id:
            target = initiator
        else:
            target = await self._get_user("пользователь не найден", user_id)
        target.freeze()
        await self._repo.save(target)

    async def delete(self, initiator_user_id: UserID, user_id: UserID) -> None:
        """Удаление пользователя.

        Args:
            initiator_user_id (UserID): Идентификатор пользователя-инициатора.
            user_id (UserID): Идентификатор удаляемого пользователя.

        Raises:
            UserNotFoundError: Инициатор или удаляемый пользователь не найдены.
        """
        initiator = await self._get_user("инициатор не найден", initiator_user_id)
        if initiator_user_id == user_id:
            if initiator.state.is_frozen():
                UserPolicyService.is_staff(initiator)
            target = initiator
        else:
            UserPolicyService.is_staff(initiator)
            target = await self._get_user("пользователь не найден", user_id)
        target.delete()
        await self._repo.save(target)

    async def _get_user(self, error_msg: str, user_id: UserID) -> User:
        user = await self._repo.by_id(user_id)
        if user is None:
            raise UserNotFoundError(msg=error_msg, data={"user_id": user_id.user_id})
        return user
