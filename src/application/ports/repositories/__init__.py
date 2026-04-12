from dataclasses import dataclass

from application.ports.repositories.personal_transaction import (
    PersonalTransactionReadRepository,
    PersonalTransactionVersionRepository,
)
from application.ports.repositories.subscription import SubscriptionRepository
from application.ports.repositories.tenant import (
    TenantReadRepository,
    TenantVersionRepository,
)
from application.ports.repositories.transaction_category import (
    TransactionCategoryReadRepository,
    TransactionCategoryVersionRepository,
)
from application.ports.repositories.user import UserReadRepository

__all__ = [
    "PersonalTransactionReadRepository",
    "PersonalTransactionRepositories",
    "PersonalTransactionVersionRepository",
    "SubscriptionRepositories",
    "SubscriptionRepository",
    "TenantReadRepository",
    "TenantRepositories",
    "TenantVersionRepository",
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
