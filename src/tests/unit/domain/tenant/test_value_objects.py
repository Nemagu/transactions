from uuid import uuid4

import pytest

from domain.errors import DomainError, ValueObjectInvalidDataError
from domain.tenant.value_objects import TenantID, TenantState, TenantStatus


def test_tenant_id_keeps_uuid_value() -> None:
    value = uuid4()

    tenant_id = TenantID(value)

    assert tenant_id.tenant_id == value


@pytest.mark.parametrize(
    ("enum_cls", "value", "expected"),
    [
        (TenantStatus, "ADMIN", TenantStatus.ADMIN),
        (TenantStatus, "tenant", TenantStatus.TENANT),
        (TenantState, "ACTIVE", TenantState.ACTIVE),
        (TenantState, "frozen", TenantState.FROZEN),
        (TenantState, "deleted", TenantState.DELETED),
    ],
    ids=[
        "status-admin",
        "status-tenant",
        "state-active",
        "state-frozen",
        "state-deleted",
    ],
)
def test_tenant_enums_restore_from_string(enum_cls, value: str, expected) -> None:
    assert enum_cls.from_str(value) == expected


@pytest.mark.parametrize(
    ("enum_value", "method_name"),
    [
        (TenantStatus.ADMIN, "is_admin"),
        (TenantStatus.TENANT, "is_tenant"),
        (TenantState.ACTIVE, "is_active"),
        (TenantState.FROZEN, "is_frozen"),
        (TenantState.DELETED, "is_deleted"),
    ],
    ids=["is-admin", "is-tenant", "is-active", "is-frozen", "is-deleted"],
)
def test_tenant_enum_helper_methods(enum_value, method_name: str) -> None:
    assert getattr(enum_value, method_name)() is True


@pytest.mark.parametrize(
    ("enum_cls", "value"),
    [
        (TenantStatus, "manager"),
        (TenantState, "archived"),
    ],
    ids=["unknown-status", "unknown-state"],
)
def test_tenant_enums_raise_for_unknown_string(enum_cls, value: str) -> None:
    with pytest.raises(ValueObjectInvalidDataError) as exc_info:
        enum_cls.from_str(value)

    assert isinstance(exc_info.value, DomainError)
