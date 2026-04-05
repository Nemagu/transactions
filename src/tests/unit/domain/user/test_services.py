from collections.abc import Callable

import pytest

from domain.user.errors import UserIdempotentError, UserNotFoundError, UserPolicyError
from domain.user.services import (
    UserEditorStateService,
    UserEditorStatusService,
    UserPolicyService,
)
from domain.user.value_objects import UserID, UserState, UserStatus


@pytest.mark.parametrize(
    ("status", "state"),
    [
        (UserStatus.USER, UserState.ACTIVE),
        (UserStatus.ADMIN, UserState.FROZEN),
        (UserStatus.ADMIN, UserState.DELETED),
    ],
    ids=["regular-user", "frozen-admin", "deleted-admin"],
)
def test_is_staff_rejects_non_editable_user(
    user_factory,
    status: UserStatus,
    state: UserState,
) -> None:
    user = user_factory(status=status, state=state)

    with pytest.raises(UserPolicyError):
        UserPolicyService.is_staff(user)


def test_is_staff_allows_active_admin(user_factory) -> None:
    user = user_factory(status=UserStatus.ADMIN, state=UserState.ACTIVE)

    assert UserPolicyService.is_staff(user) is None


@pytest.mark.parametrize(
    ("state",),
    [
        (UserState.FROZEN,),
        (UserState.DELETED,),
    ],
    ids=["frozen-user", "deleted-user"],
)
def test_can_edit_user_rejects_invalid_state(
    user_factory,
    state: UserState,
) -> None:
    user = user_factory(state=state)

    with pytest.raises(UserPolicyError):
        UserPolicyService.can_edit_user(user)


def test_can_edit_user_allows_active_user(user_factory) -> None:
    user = user_factory(state=UserState.ACTIVE)

    assert UserPolicyService.can_edit_user(user) is None


@pytest.mark.parametrize(
    ("method_name", "target_attr", "target_value", "target_status", "target_state"),
    [
        ("appoint_admin", "status", UserStatus.ADMIN, UserStatus.USER, UserState.ACTIVE),
        ("appoint_user", "status", UserStatus.USER, UserStatus.ADMIN, UserState.ACTIVE),
        ("activate", "state", UserState.ACTIVE, UserStatus.USER, UserState.FROZEN),
        ("freeze", "state", UserState.FROZEN, UserStatus.USER, UserState.ACTIVE),
        ("delete", "state", UserState.DELETED, UserStatus.USER, UserState.ACTIVE),
    ],
    ids=["appoint-admin", "appoint-user", "activate", "freeze", "delete"],
)
async def test_editor_services_update_target_and_save(
    user_factory,
    user_repository_factory,
    method_name: str,
    target_attr: str,
    target_value: UserStatus | UserState,
    target_status: UserStatus,
    target_state: UserState,
) -> None:
    initiator = user_factory(status=UserStatus.ADMIN, state=UserState.ACTIVE)
    target = user_factory(status=target_status, state=target_state)
    repository = user_repository_factory({initiator.user_id: initiator, target.user_id: target})
    service = (
        UserEditorStatusService(repository)
        if method_name in {"appoint_admin", "appoint_user"}
        else UserEditorStateService(repository)
    )

    await getattr(service, method_name)(initiator.user_id, target.user_id)

    assert getattr(target, target_attr) == target_value
    assert repository.saved_users == [target]


async def test_status_service_allows_admin_to_edit_self_to_user(
    user_factory,
    user_repository_factory,
) -> None:
    initiator = user_factory(status=UserStatus.ADMIN)
    repository = user_repository_factory({initiator.user_id: initiator})
    service = UserEditorStatusService(repository)

    await service.appoint_user(initiator.user_id, initiator.user_id)

    assert initiator.status == UserStatus.USER
    assert repository.saved_users == [initiator]


async def test_status_service_rejects_admin_self_appoint_admin_as_idempotent(
    user_factory,
    user_repository_factory,
) -> None:
    initiator = user_factory(status=UserStatus.ADMIN)
    repository = user_repository_factory({initiator.user_id: initiator})
    service = UserEditorStatusService(repository)

    with pytest.raises(UserIdempotentError):
        await service.appoint_admin(initiator.user_id, initiator.user_id)


@pytest.mark.parametrize(
    ("method_name", "target_state"),
    [
        ("appoint_admin", UserState.FROZEN),
        ("appoint_admin", UserState.DELETED),
        ("appoint_user", UserState.FROZEN),
        ("appoint_user", UserState.DELETED),
    ],
    ids=[
        "appoint-admin-frozen-target",
        "appoint-admin-deleted-target",
        "appoint-user-frozen-target",
        "appoint-user-deleted-target",
    ],
)
async def test_status_service_rejects_non_editable_target(
    user_factory,
    user_repository_factory,
    method_name: str,
    target_state: UserState,
) -> None:
    initiator = user_factory(status=UserStatus.ADMIN, state=UserState.ACTIVE)
    target = user_factory(status=UserStatus.USER, state=target_state)
    repository = user_repository_factory({initiator.user_id: initiator, target.user_id: target})
    service = UserEditorStatusService(repository)

    with pytest.raises(UserPolicyError):
        await getattr(service, method_name)(initiator.user_id, target.user_id)

    assert repository.saved_users == []
    assert target.status == UserStatus.USER


@pytest.mark.parametrize(
    ("method_name"),
    [("activate"), ("delete")],
    ids=["activate-frozen-admin", "delete-frozen-admin"],
)
async def test_state_service_rejects_frozen_admin_self_edit(
    user_factory,
    user_repository_factory,
    method_name: str,
) -> None:
    initiator = user_factory(status=UserStatus.ADMIN, state=UserState.FROZEN)
    repository = user_repository_factory({initiator.user_id: initiator})
    service = UserEditorStateService(repository)

    with pytest.raises(UserPolicyError):
        await getattr(service, method_name)(initiator.user_id, initiator.user_id)


@pytest.mark.parametrize(
    ("service_cls", "method_name"),
    [
        (UserEditorStatusService, "appoint_admin"),
        (UserEditorStatusService, "appoint_user"),
        (UserEditorStateService, "activate"),
        (UserEditorStateService, "freeze"),
        (UserEditorStateService, "delete"),
    ],
    ids=[
        "status-appoint-admin",
        "status-appoint-user",
        "state-activate",
        "state-freeze",
        "state-delete",
    ],
)
async def test_editor_services_raise_when_initiator_not_found(
    user_id_factory: Callable[[], UserID],
    user_repository_factory,
    service_cls: type[UserEditorStatusService | UserEditorStateService],
    method_name: str,
) -> None:
    repository = user_repository_factory()
    service = service_cls(repository)

    with pytest.raises(UserNotFoundError):
        await getattr(service, method_name)(user_id_factory(), user_id_factory())


@pytest.mark.parametrize(
    ("service_cls", "method_name"),
    [
        (UserEditorStatusService, "appoint_admin"),
        (UserEditorStatusService, "appoint_user"),
        (UserEditorStateService, "activate"),
        (UserEditorStateService, "freeze"),
        (UserEditorStateService, "delete"),
    ],
    ids=[
        "status-appoint-admin",
        "status-appoint-user",
        "state-activate",
        "state-freeze",
        "state-delete",
    ],
)
async def test_editor_services_raise_when_target_not_found(
    user_factory,
    user_id_factory: Callable[[], UserID],
    user_repository_factory,
    service_cls: type[UserEditorStatusService | UserEditorStateService],
    method_name: str,
) -> None:
    initiator = user_factory(status=UserStatus.ADMIN)
    repository = user_repository_factory({initiator.user_id: initiator})
    service = service_cls(repository)

    with pytest.raises(UserNotFoundError):
        await getattr(service, method_name)(initiator.user_id, user_id_factory())


async def test_activate_allows_user_self_activation_when_not_frozen(
    user_factory,
    user_repository_factory,
) -> None:
    initiator = user_factory(status=UserStatus.USER, state=UserState.DELETED)
    repository = user_repository_factory({initiator.user_id: initiator})
    service = UserEditorStateService(repository)

    await service.activate(initiator.user_id, initiator.user_id)

    assert initiator.state == UserState.ACTIVE
    assert repository.saved_users == [initiator]


async def test_delete_allows_user_self_delete_when_not_frozen(
    user_factory,
    user_repository_factory,
) -> None:
    initiator = user_factory(status=UserStatus.USER, state=UserState.ACTIVE)
    repository = user_repository_factory({initiator.user_id: initiator})
    service = UserEditorStateService(repository)

    await service.delete(initiator.user_id, initiator.user_id)

    assert initiator.state == UserState.DELETED
    assert repository.saved_users == [initiator]
