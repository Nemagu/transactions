from __future__ import annotations

import pytest

from domain.user.value_objects import UserState
from domain.value_objects import Version


@pytest.mark.asyncio
async def test_save_and_by_id_create(user_repo, user_factory, user_id_factory) -> None:
    user = user_factory()

    await user_repo.save(user)

    stored = await user_repo.by_id(user_id_factory(user.user_id.user_id))

    assert stored is not None
    assert stored.user_id == user.user_id
    assert stored.state == user.state
    assert stored.version == user.version


@pytest.mark.asyncio
async def test_save_updates_existing_user(user_repo, user_factory, user_id_factory) -> None:
    user = user_factory()
    await user_repo.save(user)

    user.new_state(UserState.FROZEN)
    user.new_version(Version(2))
    await user_repo.save(user)

    stored = await user_repo.by_id(user_id_factory(user.user_id.user_id))

    assert stored is not None
    assert stored.state == UserState.FROZEN
    assert stored.version.version == 2
