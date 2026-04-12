from dataclasses import dataclass
from typing import Self
from uuid import UUID

from domain.user import User


@dataclass(slots=True)
class UserSimpleDTO:
    user_id: UUID
    state: str
    version: int

    @classmethod
    def from_domain(cls, user: User) -> Self:
        return cls(user.user_id.user_id, user.state.value, user.version.version)
