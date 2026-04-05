from domain.personal_transaction.entity import PersonalTransaction
from domain.personal_transaction.errors import PersonalTransactionPolicyError
from domain.user.value_objects import UserID


class PersonalTransactionPolicyService:
    """Сервис проверки прав доступа для работы с персональными транзакциями."""

    @staticmethod
    def is_owner(user_id: UserID, owner_id: UserID) -> None:
        """Является ли пользователь владельцем персональной транзакции.

        Args:
            user_id (UserID): Идентификатор пользователя.
            owner_id (UserID): Идентификатор владельца транзакции.

        Raises:
            PersonalTransactionPolicyError: Пользователь не является владельцем.
        """
        if user_id != owner_id:
            raise PersonalTransactionPolicyError(
                msg="только владелец может работать с персональной транзакцией",
                data={"user_id": user_id.user_id, "owner_id": owner_id.user_id},
            )

    @staticmethod
    def can_edit(transaction: PersonalTransaction) -> None:
        """Можно ли редактировать персональную транзакцию.

        Args:
            transaction (PersonalTransaction): Транзакция, которую нужно проверить.

        Raises:
            PersonalTransactionPolicyError: Редактирование транзакции запрещено.
        """
        if transaction.state.is_deleted():
            raise PersonalTransactionPolicyError(
                msg="персональная транзакция удалена",
                data={"state": transaction.state.value},
            )
