from abc import ABC

from application.ports.unit_of_work import UnitOfWork


class BaseUseCase(ABC):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
