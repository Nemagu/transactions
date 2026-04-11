"""Доменные сервисы, связанные с персональными транзакциями."""

from src.domain.errors import EntityPolicyError
from src.domain.personal_transaction.entity import PersonalTransaction
from src.domain.user import User


class PersonalTransactionPolicyService:
    """Сервис проверки политик доступа к персональным транзакциям."""

    @staticmethod
    def is_owner(user: User, transaction: PersonalTransaction) -> None:
        """
        Args:
            user (User): Пользователь, выполняющий действие.
            transaction (PersonalTransaction): Целевая транзакция.

        Raises:
            EntityPolicyError: Пользователь не является владельцем транзакции.
        """
        if user.user_id != transaction.owner_id:
            raise EntityPolicyError(
                msg="только владелец может работать с персональной транзакцией",
                struct_name=user.aggregate_name.name,
                data={
                    "user": {"user_id": str(user.user_id.user_id)},
                    "transaction": {"owner_id": str(transaction.owner_id.user_id)},
                },
            )
