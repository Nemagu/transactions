from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID

from src.domain.errors import ValueObjectInvalidDataError


@dataclass(frozen=True)
class TenantID:
    tenant_id: UUID


class TenantStatus(StrEnum):
    ADMIN = "admin"
    TENANT = "tenant"

    def is_admin(self) -> bool:
        return self == self.__class__.ADMIN

    def is_tenant(self) -> bool:
        return self == self.__class__.TENANT

    @classmethod
    def from_str(cls, value: str) -> Self:
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise ValueObjectInvalidDataError(
            msg=(
                f"не удалось найти статус арендатора по предоставленной строке - "
                f'"{value}"'
            ),
            struct_name="статус арендатора",
            data={"status": value},
        )


class TenantState(StrEnum):
    ACTIVE = "active"
    FROZEN = "frozen"
    DELETED = "deleted"

    def is_active(self) -> bool:
        return self == self.__class__.ACTIVE

    def is_frozen(self) -> bool:
        return self == self.__class__.FROZEN

    def is_deleted(self) -> bool:
        return self == self.__class__.DELETED

    @classmethod
    def from_str(cls, value: str) -> Self:
        lower_value = value.lower()
        if lower_value in cls._value2member_map_:
            return cls(lower_value)
        raise ValueObjectInvalidDataError(
            msg=(
                f"не удалось найти состояние арендатора по предоставленной строке - "
                f'"{value}"'
            ),
            struct_name="состояние арендатора",
            data={"state": value},
        )
