from domain.errors import EntityPolicyError
from domain.personal_transaction.entity import PersonalTransaction
from domain.tenant import Tenant


class PersonalTransactionPolicyService:
    @staticmethod
    def is_owner(tenant: Tenant, transaction: PersonalTransaction) -> None:
        if tenant.tenant_id != transaction.owner_id:
            raise EntityPolicyError(
                msg="только владелец может работать с персональной транзакцией",
                struct_name=tenant.aggregate_name.name,
                data={
                    "tenant": {"tenant_id": tenant.tenant_id.tenant_id},
                    "transaction": {"owner_id": transaction.owner_id.tenant_id},
                },
            )
