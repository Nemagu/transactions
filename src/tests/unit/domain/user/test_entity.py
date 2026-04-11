import pytest

from src.domain.errors import EntityIdempotentError, EntityPolicyError
from src.domain.user.value_objects import FirstName, LastName, UserState, UserStatus


def test_user_exposes_created_state(user_factory) -> None:
    user = user_factory()

    assert user.first_name == FirstName("Ivan")
    assert user.last_name == LastName("Petrov")
    assert user.status == UserStatus.USER
    assert user.state == UserState.ACTIVE
    assert user.version.version == 1
    assert user.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "value", "expected_attr"),
    [
        ("new_first_name", FirstName("Petr"), "first_name"),
        ("new_last_name", LastName("Sidorov"), "last_name"),
    ],
    ids=["change-first-name", "change-last-name"],
)
def test_user_updates_name_fields(
    user_factory,
    method_name: str,
    value: FirstName | LastName,
    expected_attr: str,
) -> None:
    user = user_factory()

    getattr(user, method_name)(value)
    if method_name == "new_first_name":
        user.new_last_name(LastName("Sidorov"))
    else:
        user.new_first_name(FirstName("Petr"))

    assert getattr(user, expected_attr) == value
    assert user.version.version == 2
    assert user.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "value"),
    [
        ("new_first_name", FirstName("Ivan")),
        ("new_last_name", LastName("Petrov")),
    ],
    ids=["same-first-name", "same-last-name"],
)
def test_user_rejects_idempotent_name_changes(
    user_factory,
    method_name: str,
    value: FirstName | LastName,
) -> None:
    user = user_factory()

    with pytest.raises(EntityIdempotentError):
        getattr(user, method_name)(value)


@pytest.mark.parametrize(
    ("method_name", "initial_status", "expected_status"),
    [
        ("appoint_admin", UserStatus.USER, UserStatus.ADMIN),
        ("appoint_user", UserStatus.ADMIN, UserStatus.USER),
    ],
    ids=["appoint-admin", "appoint-user"],
)
def test_user_changes_status(
    user_factory,
    method_name: str,
    initial_status: UserStatus,
    expected_status: UserStatus,
) -> None:
    user = user_factory(status=initial_status)

    getattr(user, method_name)()
    assert user.status == expected_status
    assert user.version.version == 2
    assert user.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "status"),
    [
        ("appoint_admin", UserStatus.ADMIN),
        ("appoint_user", UserStatus.USER),
    ],
    ids=["admin-to-admin", "user-to-user"],
)
def test_user_rejects_idempotent_status_changes(
    user_factory,
    method_name: str,
    status: UserStatus,
) -> None:
    user = user_factory(status=status)

    with pytest.raises(EntityIdempotentError):
        getattr(user, method_name)()


@pytest.mark.parametrize(
    ("method_name", "initial_state", "expected_state"),
    [
        ("activate", UserState.FROZEN, UserState.ACTIVE),
        ("freeze", UserState.ACTIVE, UserState.FROZEN),
        ("delete", UserState.ACTIVE, UserState.DELETED),
    ],
    ids=["activate-user", "freeze-user", "delete-user"],
)
def test_user_changes_state(
    user_factory,
    method_name: str,
    initial_state: UserState,
    expected_state: UserState,
) -> None:
    user = user_factory(state=initial_state)

    getattr(user, method_name)()

    assert user.state == expected_state
    assert user.version.version == 2
    assert user.original_version.version == 1


def test_user_starts_new_version_cycle_after_persist(user_factory) -> None:
    user = user_factory()

    user.new_first_name(FirstName("Petr"))
    user.mark_persisted()
    user.new_last_name(LastName("Sidorov"))

    assert user.version.version == 3
    assert user.original_version.version == 2


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("activate", UserState.ACTIVE),
        ("freeze", UserState.FROZEN),
        ("delete", UserState.DELETED),
    ],
    ids=["activate-active", "freeze-frozen", "delete-deleted"],
)
def test_user_rejects_idempotent_state_changes(
    user_factory,
    method_name: str,
    state: UserState,
) -> None:
    user = user_factory(state=state)

    with pytest.raises(EntityIdempotentError):
        getattr(user, method_name)()


@pytest.mark.parametrize(
    ("status", "state"),
    [
        (UserStatus.USER, UserState.ACTIVE),
        (UserStatus.ADMIN, UserState.FROZEN),
        (UserStatus.ADMIN, UserState.DELETED),
    ],
    ids=["regular-user", "frozen-admin", "deleted-admin"],
)
def test_user_raise_staff_rejects_non_staff_or_unavailable_user(
    user_factory,
    status: UserStatus,
    state: UserState,
) -> None:
    user = user_factory(status=status, state=state)

    with pytest.raises(EntityPolicyError):
        user.raise_staff()


def test_user_raise_staff_allows_active_admin(user_factory) -> None:
    user = user_factory(status=UserStatus.ADMIN, state=UserState.ACTIVE)

    assert user.raise_staff() is None
