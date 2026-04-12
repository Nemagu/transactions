import pytest

from domain.errors import (
    EntityIdempotentError,
    EntityInvalidDataError,
    EntityPolicyError,
)
from domain.tenant.value_objects import TenantState, TenantStatus


def test_tenant_exposes_created_state(local_tenant_factory) -> None:
    tenant = local_tenant_factory()

    assert tenant.status == TenantStatus.TENANT
    assert tenant.state == TenantState.ACTIVE
    assert tenant.version.version == 1
    assert tenant.original_version.version == 1


@pytest.mark.parametrize(
    ("method_name", "initial_status", "expected_status"),
    [
        ("appoint_admin", TenantStatus.TENANT, TenantStatus.ADMIN),
        ("appoint_tenant", TenantStatus.ADMIN, TenantStatus.TENANT),
    ],
    ids=["appoint-admin", "appoint-tenant"],
)
def test_tenant_changes_status(
    local_tenant_factory,
    method_name: str,
    initial_status: TenantStatus,
    expected_status: TenantStatus,
) -> None:
    tenant = local_tenant_factory(status=initial_status)

    getattr(tenant, method_name)()

    assert tenant.status == expected_status
    assert tenant.version.version == 2


@pytest.mark.parametrize(
    ("method_name", "status"),
    [
        ("appoint_admin", TenantStatus.ADMIN),
        ("appoint_tenant", TenantStatus.TENANT),
    ],
    ids=["admin-to-admin", "tenant-to-tenant"],
)
def test_tenant_rejects_idempotent_status_changes(
    local_tenant_factory,
    method_name: str,
    status: TenantStatus,
) -> None:
    tenant = local_tenant_factory(status=status)

    with pytest.raises(EntityIdempotentError):
        getattr(tenant, method_name)()


@pytest.mark.parametrize(
    ("method_name", "initial_state", "expected_state"),
    [
        ("activate", TenantState.FROZEN, TenantState.ACTIVE),
        ("freeze", TenantState.ACTIVE, TenantState.FROZEN),
        ("delete", TenantState.ACTIVE, TenantState.DELETED),
    ],
    ids=["activate-tenant", "freeze-tenant", "delete-tenant"],
)
def test_tenant_changes_state(
    local_tenant_factory,
    method_name: str,
    initial_state: TenantState,
    expected_state: TenantState,
) -> None:
    tenant = local_tenant_factory(state=initial_state)

    getattr(tenant, method_name)()

    assert tenant.state == expected_state
    assert tenant.version.version == 2


def test_tenant_starts_new_version_cycle_after_persist(local_tenant_factory) -> None:
    tenant = local_tenant_factory()

    tenant.appoint_admin()
    tenant.mark_persisted()
    tenant.freeze()

    assert tenant.version.version == 3
    assert tenant.original_version.version == 2


def test_tenant_new_state_changes_state(local_tenant_factory) -> None:
    tenant = local_tenant_factory(state=TenantState.ACTIVE)

    tenant.new_state(TenantState.DELETED)

    assert tenant.state == TenantState.DELETED
    assert tenant.version.version == 2


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("new_state", TenantState.ACTIVE),
        ("activate", TenantState.ACTIVE),
        ("freeze", TenantState.FROZEN),
        ("delete", TenantState.DELETED),
    ],
    ids=["new-state-active", "activate-active", "freeze-frozen", "delete-deleted"],
)
def test_tenant_rejects_idempotent_state_changes(
    local_tenant_factory,
    method_name: str,
    state: TenantState,
) -> None:
    tenant = local_tenant_factory(state=state)

    with pytest.raises(EntityIdempotentError):
        if method_name == "new_state":
            tenant.new_state(state)
        else:
            getattr(tenant, method_name)()


@pytest.mark.parametrize(
    ("status", "state"),
    [
        (TenantStatus.TENANT, TenantState.ACTIVE),
        (TenantStatus.ADMIN, TenantState.FROZEN),
        (TenantStatus.ADMIN, TenantState.DELETED),
    ],
    ids=["regular-tenant", "frozen-admin", "deleted-admin"],
)
def test_tenant_raise_staff_rejects_unavailable_or_non_admin(
    local_tenant_factory,
    status: TenantStatus,
    state: TenantState,
) -> None:
    tenant = local_tenant_factory(status=status, state=state)

    with pytest.raises(EntityPolicyError):
        tenant.raise_staff()


def test_tenant_raise_staff_allows_active_admin(local_tenant_factory) -> None:
    tenant = local_tenant_factory(
        status=TenantStatus.ADMIN,
        state=TenantState.ACTIVE,
    )

    assert tenant.raise_staff() is None


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("appoint_admin", TenantState.DELETED),
        ("appoint_admin", TenantState.FROZEN),
        ("appoint_tenant", TenantState.DELETED),
        ("appoint_tenant", TenantState.FROZEN),
    ],
    ids=[
        "appoint-admin-deleted",
        "appoint-admin-frozen",
        "appoint-tenant-deleted",
        "appoint-tenant-frozen",
    ],
)
def test_tenant_rejects_status_changes_when_state_invalid(
    local_tenant_factory,
    method_name: str,
    state: TenantState,
) -> None:
    tenant = local_tenant_factory(state=state)

    with pytest.raises(EntityInvalidDataError):
        getattr(tenant, method_name)()
