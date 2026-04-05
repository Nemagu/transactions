from dataclasses import dataclass

from domain.errors import VersionError


@dataclass(frozen=True)
class Version:
    """Версия агрегата.

    Args:
        version (int): Версия.

    Raises:
        VersionError: Версия не может быть отрицательной.
    """

    version: int

    def __post_init__(self) -> None:
        if self.version < 1:
            raise VersionError(
                msg=(
                    f'версия не может быть меньше 1, указана версия - "{self.version}"'
                )
            )
