from src.domain.errors import EntityAlreadyExistsError, EntityPolicyError
from src.domain.tenant import Tenant
from src.domain.transaction_category.entity import TransactionCategory
from src.domain.transaction_category.repository import TransactionCategoryRepository
from src.domain.transaction_category.value_objects import TransactionCategoryName


class TransactionCategoryPolicyService:
    @staticmethod
    def is_owner(tenant: Tenant, category: TransactionCategory) -> None:
        if tenant.tenant_id != category.owner_id:
            raise EntityPolicyError(
                msg="только владелец может работать с категорией транзакции",
                struct_name=tenant.aggregate_name.name,
                data={
                    "tenant": {"tenant_id": str(tenant.tenant_id.tenant_id)},
                    "category": {
                        "category_id": str(
                            category.category_id.category_id,
                        ),
                        "owner_id": str(category.owner_id.tenant_id),
                    },
                },
            )


class TransactionCategoryUniquenessService:
    def __init__(self, repository: TransactionCategoryRepository) -> None:
        self._repo = repository

    async def ensure_unique(
        self,
        tenant: Tenant,
        name: TransactionCategoryName,
    ) -> None:
        category = await self._repo.by_owner_id_name(tenant.tenant_id, name)
        if category is not None:
            if category.state.is_deleted():
                raise EntityAlreadyExistsError(
                    msg="название категории транзакции уже используется, но она была ранее удалена",
                    struct_name=category.aggregate_name.name,
                    data={
                        "category_id": str(category.category_id.category_id),
                        "name": name.name,
                    },
                )
            raise EntityAlreadyExistsError(
                msg="название категории транзакции уже используется",
                struct_name=category.aggregate_name.name,
                data={
                    "category_id": str(category.category_id.category_id),
                    "name": name.name,
                },
            )
