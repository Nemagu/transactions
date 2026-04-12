from domain.entities import Entity
from domain.errors import (
    EntityIdempotentError,
    EntityInvalidDataError,
    EntityPolicyError,
)
from domain.tenant.value_objects import TenantID, TenantState, TenantStatus
from domain.value_objects import AggregateName, Version


class Tenant(Entity):
    def __init__(
        self,
        tenant_id: TenantID,
        status: TenantStatus,
        state: TenantState,
        version: Version,
    ):
        super().__init__(
            version,
            AggregateName("арендатор"),
            "_tenant_id",
            "tenant",
            ["_tenant_id", "_status", "_state"],
        )
        self._tenant_id = tenant_id
        self._status = status
        self._state = state

    @property
    def tenant_id(self) -> TenantID:
        return self._tenant_id

    @property
    def status(self) -> TenantStatus:
        return self._status

    @property
    def state(self) -> TenantState:
        return self._state

    def raise_staff(self) -> None:
        if self._state.is_deleted():
            raise EntityPolicyError(
                **self._error_data(
                    "вы удалены",
                    {"state": self._state.value},
                )
            )
        if self._state.is_frozen():
            raise EntityPolicyError(
                **self._error_data(
                    "вы заморожены",
                    {
                        "tenant_id": self._tenant_id.tenant_id,
                        "state": self._state.value,
                    },
                )
            )
        if not self._status.is_admin():
            raise EntityPolicyError(
                **self._error_data(
                    "вы не являетесь администратором",
                    {"state": self._state.value},
                )
            )

    def appoint_admin(self) -> None:
        self._check_state()
        if self._status.is_admin():
            raise EntityIdempotentError(
                **self._error_data(
                    "арендатор уже является администратором",
                    {"status": self._status.value},
                )
            )
        self._status = TenantStatus.ADMIN
        self._update_version()

    def appoint_tenant(self) -> None:
        self._check_state()
        if self._status.is_tenant():
            raise EntityIdempotentError(
                **self._error_data(
                    "арендатор уже является пользователем",
                    {"status": self._status.value},
                )
            )
        self._status = TenantStatus.TENANT
        self._update_version()

    def activate(self) -> None:
        if self._state.is_active():
            raise EntityIdempotentError(
                **self._error_data(
                    "арендатор уже является активным",
                    {"state": self._state.value},
                )
            )
        self._state = TenantState.ACTIVE
        self._update_version()

    def freeze(self) -> None:
        if self._state.is_frozen():
            raise EntityIdempotentError(
                **self._error_data(
                    "арендатор уже является замороженным",
                    {"state": self._state.value},
                )
            )
        self._state = TenantState.FROZEN
        self._update_version()

    def delete(self) -> None:
        if self._state.is_deleted():
            raise EntityIdempotentError(
                **self._error_data(
                    "арендатор уже является удаленным",
                    {"state": self._state.value},
                )
            )
        self._state = TenantState.DELETED
        self._update_version()

    def _check_state(self) -> None:
        if self._state.is_deleted():
            raise EntityInvalidDataError(
                **self._error_data(
                    "арендатор удален",
                    {"state": self._state.value},
                )
            )
        if self._state.is_frozen():
            raise EntityInvalidDataError(
                **self._error_data(
                    "арендатор заморожен",
                    {"state": self._state.value},
                )
            )
