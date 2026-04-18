from dataclasses import dataclass

from application.ports.repositories.personal_transaction import (
    PersonalTransactionEvent,
    PersonalTransactionReadRepository,
    PersonalTransactionVersionRepository,
)
from application.ports.repositories.tenant import (
    TenantEvent,
    TenantReadRepository,
    TenantSubscriptionRepository,
    TenantVersionRepository,
)
from application.ports.repositories.transaction_category import (
    TransactionCategoryEvent,
    TransactionCategoryReadRepository,
    TransactionCategoryVersionRepository,
)
from application.ports.repositories.user import UserReadRepository

__all__ = [
    "PersonalTransactionEvent",
    "PersonalTransactionReadRepository",
    "PersonalTransactionRepositories",
    "PersonalTransactionVersionRepository",
    "TenantEvent",
    "TenantReadRepository",
    "TenantRepositories",
    "TenantSubscriptionRepository",
    "TenantVersionRepository",
    "TransactionCategoryEvent",
    "TransactionCategoryReadRepository",
    "TransactionCategoryRepositories",
    "TransactionCategoryVersionRepository",
    "UserReadRepository",
    "UserRepositories",
]


@dataclass(slots=True)
class UserRepositories:
    read: UserReadRepository


@dataclass(slots=True)
class TenantRepositories:
    read: TenantReadRepository
    version: TenantVersionRepository
    subscription: TenantSubscriptionRepository


@dataclass(slots=True)
class TransactionCategoryRepositories:
    read: TransactionCategoryReadRepository
    version: TransactionCategoryVersionRepository


@dataclass(slots=True)
class PersonalTransactionRepositories:
    read: PersonalTransactionReadRepository
    version: PersonalTransactionVersionRepository
