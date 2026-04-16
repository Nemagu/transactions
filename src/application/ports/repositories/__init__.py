from dataclasses import dataclass

from application.ports.repositories.personal_transaction import (
    PersonalTransactionEvent,
    PersonalTransactionReadRepository,
    PersonalTransactionVersionRepository,
)
from application.ports.repositories.subscription import SubscriptionRepository
from application.ports.repositories.tenant import (
    TenantEvent,
    TenantReadRepository,
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
    "SubscriptionRepositories",
    "SubscriptionRepository",
    "TenantEvent",
    "TenantReadRepository",
    "TenantRepositories",
    "TenantVersionRepository",
    "TransactionCategoryEvent",
    "TransactionCategoryReadRepository",
    "TransactionCategoryRepositories",
    "TransactionCategoryVersionRepository",
    "UserReadRepository",
    "UserRepositories",
]


@dataclass(slots=True)
class SubscriptionRepositories:
    common: SubscriptionRepository


@dataclass(slots=True)
class UserRepositories:
    read: UserReadRepository


@dataclass(slots=True)
class TenantRepositories:
    read: TenantReadRepository
    version: TenantVersionRepository


@dataclass(slots=True)
class TransactionCategoryRepositories:
    read: TransactionCategoryReadRepository
    version: TransactionCategoryVersionRepository


@dataclass(slots=True)
class PersonalTransactionRepositories:
    read: PersonalTransactionReadRepository
    version: PersonalTransactionVersionRepository
