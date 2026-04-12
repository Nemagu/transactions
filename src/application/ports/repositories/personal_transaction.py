from abc import ABC, abstractmethod

from domain.personal_transaction import PersonalTransaction, PersonalTransactionID


class PersonalTransactionReadRepository(ABC):
    @abstractmethod
    async def by_id(
        self, transaction_id: PersonalTransactionID
    ) -> PersonalTransaction | None: ...

    @abstractmethod
    async def save(self, transaction: PersonalTransaction) -> None: ...


class PersonalTransactionVersionRepository(ABC):
    @abstractmethod
    async def save(self, transaction: PersonalTransaction) -> None: ...
