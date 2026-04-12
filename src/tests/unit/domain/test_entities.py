import pytest

from domain.entities import Entity, EntityWithState
from domain.errors import EntityIdempotentError, EntityInvalidDataError
from domain.value_objects import AggregateName, State, Version


class StubEntity(Entity):
    def __init__(self, version: Version) -> None:
        super().__init__(
            version=version,
            aggregate_name=AggregateName("тестовая сущность"),
            id_private_field="_entity_id",
            main_error_field_name="entity",
            extend_repr_fields=["_entity_id", "_payload"],
        )
        self._entity_id = "entity-1"
        self._payload = "value"

    @property
    def entity_id(self) -> str:
        return self._entity_id


class StubEntityWithState(EntityWithState):
    def __init__(self, state: State, version: Version) -> None:
        super().__init__(
            state=state,
            version=version,
            aggregate_name=AggregateName("сущность с состоянием"),
            id_private_field="_entity_id",
            main_error_field_name="entity",
            extend_repr_fields=["_entity_id", "_payload"],
        )
        self._entity_id = "entity-1"
        self._payload = "value"

    @property
    def entity_id(self) -> str:
        return self._entity_id


class StubEntityWithoutMainErrorField(Entity):
    def __init__(self) -> None:
        super().__init__(
            version=Version(1),
            aggregate_name=AggregateName("fallback сущность"),
            id_private_field="_entity_id",
            extend_repr_fields=["_entity_id"],
        )
        self._entity_id = "entity-1"

    @property
    def entity_id(self) -> str:
        return self._entity_id


def test_entity_exposes_version() -> None:
    entity = StubEntity(version=Version(2))

    assert entity.version == Version(2)
    assert entity.original_version == Version(2)
    assert entity.aggregate_name == AggregateName("тестовая сущность")


def test_entity_updates_version_only_once_per_cycle() -> None:
    entity = StubEntity(version=Version(2))

    entity._update_version()
    entity._update_version()

    assert entity.version == Version(3)
    assert entity.original_version == Version(2)


def test_entity_marks_persisted() -> None:
    entity = StubEntity(version=Version(2))

    entity._update_version()
    entity.mark_persisted()
    entity._update_version()

    assert entity.version == Version(4)
    assert entity.original_version == Version(3)


def test_entity_repr_contains_registered_fields() -> None:
    entity = StubEntity(version=Version(2))

    assert repr(entity) == (
        "StubEntity(_version: Version(version=2), "
        "_aggregate_name: AggregateName(name='тестовая сущность'), "
        "_entity_id: entity-1, _payload: value)"
    )
    assert str(entity) == repr(entity)


def test_entity_uses_fallback_main_error_field_name() -> None:
    entity = StubEntityWithoutMainErrorField()

    assert entity._error_data("ошибка") == {
        "msg": "ошибка",
        "struct_name": "fallback сущность",
        "data": {"entity": {"entity_id": "entity-1"}},
    }


def test_entity_with_state_changes_state_once_per_cycle() -> None:
    entity = StubEntityWithState(state=State.ACTIVE, version=Version(3))

    entity.delete()
    entity.activate()

    assert entity.state == State.ACTIVE
    assert entity.version == Version(4)
    assert entity.original_version == Version(3)


def test_entity_with_state_updates_state_via_new_state() -> None:
    entity = StubEntityWithState(state=State.ACTIVE, version=Version(1))

    entity.new_state(State.DELETED)

    assert entity.state == State.DELETED
    assert entity.version == Version(2)


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("new_state", State.ACTIVE),
        ("activate", State.ACTIVE),
        ("delete", State.DELETED),
    ],
    ids=["same-state", "activate-active", "delete-deleted"],
)
def test_entity_with_state_rejects_idempotent_actions(
    method_name: str,
    state: State,
) -> None:
    entity = StubEntityWithState(state=state, version=Version(1))

    with pytest.raises(EntityIdempotentError):
        if method_name == "new_state":
            entity.new_state(state)
        else:
            getattr(entity, method_name)()


def test_entity_with_state_rejects_work_with_deleted_state() -> None:
    entity = StubEntityWithState(state=State.DELETED, version=Version(1))

    with pytest.raises(EntityInvalidDataError):
        entity._check_state(msg="редактирование запрещено")
