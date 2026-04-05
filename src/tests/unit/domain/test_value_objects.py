import pytest

from domain.errors import VersionError
from domain.value_objects import Version


def test_version_accepts_positive_number() -> None:
    assert Version(1).version == 1
    assert Version(7).version == 7


def test_version_rejects_zero_and_negative_number() -> None:
    with pytest.raises(VersionError):
        Version(0)

    with pytest.raises(VersionError):
        Version(-1)
