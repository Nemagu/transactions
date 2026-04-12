import pytest

from domain.errors import EntityIdempotentError, EntityInvalidDataError
from domain.projections import Projection, ProjectionWithState
from domain.value_objects import ProjectionName, State, Version


class StubProjection(Projection):
    def __init__(self, version: Version) -> None:
        super().__init__(
            version=version,
            projection_name=ProjectionName("тестовая проекция"),
            id_private_field="_projection_id",
            main_error_field_name="projection",
            extend_repr_fields=["_projection_id", "_payload"],
        )
        self._projection_id = "projection-1"
        self._payload = "value"

    @property
    def projection_id(self) -> str:
        return self._projection_id


class StubProjectionWithState(ProjectionWithState):
    def __init__(self, state: State, version: Version) -> None:
        super().__init__(
            state=state,
            version=version,
            projection_name=ProjectionName("проекция с состоянием"),
            id_private_field="_projection_id",
            main_error_field_name="projection",
            extend_repr_fields=["_projection_id", "_payload"],
        )
        self._projection_id = "projection-1"
        self._payload = "value"

    @property
    def projection_id(self) -> str:
        return self._projection_id


class StubProjectionWithoutMainErrorField(Projection):
    def __init__(self, version: Version) -> None:
        super().__init__(
            version=version,
            projection_name=ProjectionName("fallback проекция"),
            id_private_field="_projection_id",
            extend_repr_fields=["_projection_id"],
        )
        self._projection_id = "projection-1"

    @property
    def projection_id(self) -> str:
        return self._projection_id


def test_projection_updates_version() -> None:
    projection = StubProjection(version=Version(2))

    projection.new_version(Version(3))

    assert projection.version == Version(3)


def test_projection_repr_contains_registered_fields() -> None:
    projection = StubProjection(version=Version(2))

    assert repr(projection) == (
        "StubProjection(_version: Version(version=2), "
        "_projection_name: ProjectionName(name='тестовая проекция'), "
        "_projection_id: projection-1, _payload: value)"
    )
    assert str(projection) == repr(projection)


def test_projection_uses_fallback_main_error_field_name() -> None:
    projection = StubProjectionWithoutMainErrorField(version=Version(1))

    assert projection._error_data("ошибка") == {
        "msg": "ошибка",
        "struct_name": "fallback проекция",
        "data": {"projection": {"projection_id": "projection-1"}},
    }


def test_projection_rejects_same_version() -> None:
    projection = StubProjection(version=Version(1))

    with pytest.raises(EntityIdempotentError):
        projection.new_version(Version(1))


def test_projection_rejects_lower_version() -> None:
    projection = StubProjection(version=Version(3))

    with pytest.raises(EntityInvalidDataError):
        projection.new_version(Version(2))


@pytest.mark.parametrize(
    ("method_name", "state"),
    [
        ("new_state", State.ACTIVE),
        ("activate", State.ACTIVE),
        ("delete", State.DELETED),
    ],
    ids=["same-state", "activate-active", "delete-deleted"],
)
def test_projection_with_state_rejects_idempotent_actions(
    method_name: str,
    state: State,
) -> None:
    projection = StubProjectionWithState(state=state, version=Version(1))

    with pytest.raises(EntityIdempotentError):
        if method_name == "new_state":
            projection.new_state(state)
        else:
            getattr(projection, method_name)()


def test_projection_with_state_changes_state_without_version_update() -> None:
    projection = StubProjectionWithState(state=State.DELETED, version=Version(2))

    projection.activate()

    assert projection.state == State.ACTIVE
    assert projection.version == Version(2)


def test_projection_with_state_updates_state_via_new_state() -> None:
    projection = StubProjectionWithState(state=State.ACTIVE, version=Version(2))

    projection.new_state(State.DELETED)

    assert projection.state == State.DELETED
    assert projection.version == Version(2)


def test_projection_with_state_deletes_without_version_update() -> None:
    projection = StubProjectionWithState(state=State.ACTIVE, version=Version(2))

    projection.delete()

    assert projection.state == State.DELETED
    assert projection.version == Version(2)
