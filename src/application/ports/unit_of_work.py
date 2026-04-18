from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from application.ports.repositories import (
    PersonalTransactionRepositories,
    TenantRepositories,
    TransactionCategoryRepositories,
    UserRepositories,
)

__all__ = ["UnitOfWork"]


class UnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    @property
    @abstractmethod
    def user_repositories(self) -> UserRepositories: ...

    @property
    @abstractmethod
    def tenant_repositories(self) -> TenantRepositories: ...

    @property
    @abstractmethod
    def category_repositories(self) -> TransactionCategoryRepositories: ...

    @property
    @abstractmethod
    def transaction_repositories(self) -> PersonalTransactionRepositories: ...
