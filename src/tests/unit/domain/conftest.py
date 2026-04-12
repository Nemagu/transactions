from collections.abc import Callable
from uuid import UUID, uuid4

import pytest

from domain.tenant.entity import Tenant
from domain.tenant.value_objects import TenantID, TenantState, TenantStatus
from domain.user.projection import User
from domain.user.value_objects import UserID, UserState
from domain.value_objects import Version


@pytest.fixture
def tenant_id_factory() -> Callable[[UUID | None], TenantID]:
    def factory(value: UUID | None = None) -> TenantID:
        return TenantID(value or uuid4())

    return factory


@pytest.fixture
def tenant_factory(
    tenant_id_factory: Callable[[UUID | None], TenantID],
) -> Callable[..., Tenant]:
    def factory(
        *,
        tenant_id: TenantID | None = None,
        status: TenantStatus = TenantStatus.TENANT,
        state: TenantState = TenantState.ACTIVE,
        version: int = 1,
    ) -> Tenant:
        return Tenant(
            tenant_id=tenant_id or tenant_id_factory(),
            status=status,
            state=state,
            version=Version(version),
        )

    return factory


@pytest.fixture
def user_id_factory() -> Callable[[UUID | None], UserID]:
    def factory(value: UUID | None = None) -> UserID:
        return UserID(value or uuid4())

    return factory


@pytest.fixture
def user_factory(
    user_id_factory: Callable[[UUID | None], UserID],
) -> Callable[..., User]:
    def factory(
        *,
        user_id: UserID | None = None,
        state: UserState = UserState.ACTIVE,
        version: int = 1,
    ) -> User:
        return User(
            user_id=user_id or user_id_factory(),
            state=state,
            version=Version(version),
        )

    return factory
