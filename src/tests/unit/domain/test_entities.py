from domain.entities import Entity
from domain.value_objects import Version


def test_entity_exposes_version() -> None:
    entity = Entity(version=Version(2))

    assert entity.version == Version(2)
    assert entity.original_version == Version(2)


def test_entity_updates_version() -> None:
    entity = Entity(version=Version(2))

    entity._update_version()
    entity._update_version()

    assert entity.version == Version(3)
    assert entity.original_version == Version(2)


def test_entity_marks_persisted() -> None:
    entity = Entity(version=Version(2))

    entity._update_version()
    entity.mark_persisted()
    entity._update_version()

    assert entity.version == Version(4)
    assert entity.original_version == Version(3)
