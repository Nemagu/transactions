from domain.value_objects import Version


class Entity:
    """Базовый агрегат."""

    def __init__(self, version: Version):
        """
        Args:
            version (Version): Текущая версия агрегата.
        """
        self._version = version
        self._original_version = version

    @property
    def version(self) -> Version:
        """
        Returns:
            Version: Текущая версия агрегата.
        """
        return self._version

    @property
    def original_version(self) -> Version:
        """
        Returns:
            Version: Исходная версия агрегата до редактирования.
        """
        return self._original_version

    def _update_version(self) -> None:
        """Обновление версии агрегата после первого изменения."""
        if self._version == self._original_version:
            self._version = Version(self._original_version.version + 1)

    def mark_persisted(self) -> None:
        """Отметка агрегата как сохраненный."""
        self._original_version = self._version
