from dataclasses import dataclass

from application.ports.repositories.personal_transaction import (
    PersonalTransactionEvent,
    PersonalTransactionReadRepository,
    PersonalTransactionVersionDTO,
    PersonalTransactionVersionRepository,
)
from application.ports.repositories.tenant import (
    TenantEvent,
    TenantReadRepository,
    TenantSubscriptionRepository,
    TenantVersionDTO,
    TenantVersionRepository,
)
from application.ports.repositories.transaction_category import (
    TransactionCategoryEvent,
    TransactionCategoryReadRepository,
    TransactionCategoryVersionDTO,
    TransactionCategoryVersionRepository,
)
from application.ports.repositories.user import UserReadRepository

__all__ = [
    "PersonalTransactionEvent",
    "PersonalTransactionReadRepository",
    "PersonalTransactionRepositories",
    "PersonalTransactionVersionDTO",
    "PersonalTransactionVersionRepository",
    "TenantEvent",
    "TenantReadRepository",
    "TenantRepositories",
    "TenantSubscriptionRepository",
    "TenantVersionDTO",
    "TenantVersionRepository",
    "TransactionCategoryEvent",
    "TransactionCategoryReadRepository",
    "TransactionCategoryRepositories",
    "TransactionCategoryVersionDTO",
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
