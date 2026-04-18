from __future__ import annotations

from uuid import uuid7

import pytest

from application.commands.private.user import (
    UserCreationCommand,
    UserCreationUseCase,
    UserUpdateCommand,
    UserUpdateUseCase,
)
from application.errors import AppNotFoundError
from domain.user import UserID, UserState


@pytest.mark.asyncio
async def test_user_creation_and_update_use_cases(uow_factory, user_repo) -> None:
    user_id = uuid7()

    create_dto = await UserCreationUseCase(uow_factory()).execute(
        UserCreationCommand(
            user_id=user_id,
            state=UserState.ACTIVE.value,
            version=1,
        )
    )
    update_dto = await UserUpdateUseCase(uow_factory()).execute(
        UserUpdateCommand(
            user_id=user_id,
            state=UserState.FROZEN.value,
            version=2,
        )
    )

    assert create_dto.user_id == user_id
    assert create_dto.state == UserState.ACTIVE.value
    assert create_dto.version == 1

    assert update_dto.user_id == user_id
    assert update_dto.state == UserState.FROZEN.value
    assert update_dto.version == 2

    stored = await user_repo.by_id(UserID(user_id))
    assert stored is not None
    assert stored.state == UserState.FROZEN
    assert stored.version.version == 2


@pytest.mark.asyncio
async def test_user_update_use_case_raises_for_missing_user(uow_factory) -> None:
    with pytest.raises(AppNotFoundError):
        await UserUpdateUseCase(uow_factory()).execute(
            UserUpdateCommand(
                user_id=uuid7(),
                state=UserState.ACTIVE.value,
                version=1,
            )
        )

