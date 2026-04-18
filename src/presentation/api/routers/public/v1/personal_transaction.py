from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends

from application.commands.public.personal_transaction import (
    PersonalTransactionCreationUseCase,
    PersonalTransactionDeletionCommand,
    PersonalTransactionDeletionUseCase,
    PersonalTransactionRestorationCommand,
    PersonalTransactionRestorationUseCase,
    PersonalTransactionUpdateUseCase,
)
from application.dto import LimitOffsetPaginator, MoneyAmountDTO
from application.queries.public.personal_transaction import (
    PersonalTransactionLastVersionQuery,
    PersonalTransactionLastVersionsQuery,
    PersonalTransactionLastVersionsUseCase,
    PersonalTransactionLastVersionUseCase,
    PersonalTransactionVersionQuery,
    PersonalTransactionVersionsQuery,
    PersonalTransactionVersionsUseCase,
    PersonalTransactionVersionUseCase,
)
from infrastructure.db.postgres import PostgresUnitOfWork
from presentation.api.dependencies import db_unit_of_work, user_id_extractor
from presentation.api.models.paginator_result import LimitOffsetPaginatorResult
from presentation.api.models.personal_transaction import (
    PersonalTransactionCreationRequest,
    PersonalTransactionSimpleResponse,
    PersonalTransactionUpdateRequest,
    PersonalTransactionVersionSimpleResponse,
)

transaction_router = APIRouter(
    prefix="/personal-transactions",
    tags=["Personal transaction"],
)


@transaction_router.get("")
async def get_transactions(
    limit: int = 20,
    offset: int = 0,
    transaction_id: list[UUID] | None = None,
    category_id: list[UUID] | None = None,
    transaction_type: list[str] | None = None,
    from_money_amount: Decimal | None = None,
    from_money_currency: str | None = None,
    to_money_amount: Decimal | None = None,
    to_money_currency: str | None = None,
    from_transaction_time: datetime | None = None,
    to_transaction_time: datetime | None = None,
    state: list[str] | None = None,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> LimitOffsetPaginatorResult[PersonalTransactionSimpleResponse]:
    paginator = LimitOffsetPaginator(limit, offset)
    from_money = None
    if from_money_amount and from_money_currency:
        from_money = MoneyAmountDTO(from_money_amount, from_money_currency)
    to_money = None
    if to_money_amount and to_money_currency:
        to_money = MoneyAmountDTO(to_money_amount, to_money_currency)
    query = PersonalTransactionLastVersionsQuery(
        user_id,
        paginator,
        transaction_id,
        category_id,
        transaction_type,
        from_money,
        to_money,
        from_transaction_time,
        to_transaction_time,
        state,
    )
    uc = PersonalTransactionLastVersionsUseCase(uow)
    result, count = await uc.execute(query)
    result = [PersonalTransactionSimpleResponse.from_dto(d) for d in result]
    return LimitOffsetPaginatorResult(count=count, results=result)


@transaction_router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> PersonalTransactionSimpleResponse:
    query = PersonalTransactionLastVersionQuery(user_id, transaction_id)
    uc = PersonalTransactionLastVersionUseCase(uow)
    result = await uc.execute(query)
    return PersonalTransactionSimpleResponse.from_dto(result)


@transaction_router.get("/versions/{transaction_id}")
async def get_transactions_versions(
    transaction_id: UUID,
    limit: int = 20,
    offset: int = 0,
    category_id: list[UUID] | None = None,
    transaction_type: list[str] | None = None,
    from_money_amount: Decimal | None = None,
    from_money_currency: str | None = None,
    to_money_amount: Decimal | None = None,
    to_money_currency: str | None = None,
    from_transaction_time: datetime | None = None,
    to_transaction_time: datetime | None = None,
    state: list[str] | None = None,
    from_version: int | None = None,
    to_version: int | None = None,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> LimitOffsetPaginatorResult[PersonalTransactionVersionSimpleResponse]:
    paginator = LimitOffsetPaginator(limit, offset)
    from_money = None
    if from_money_amount and from_money_currency:
        from_money = MoneyAmountDTO(from_money_amount, from_money_currency)
    to_money = None
    if to_money_amount and to_money_currency:
        to_money = MoneyAmountDTO(to_money_amount, to_money_currency)
    query = PersonalTransactionVersionsQuery(
        user_id,
        paginator,
        transaction_id,
        category_id,
        transaction_type,
        from_money,
        to_money,
        from_transaction_time,
        to_transaction_time,
        state,
        from_version,
        to_version,
    )
    uc = PersonalTransactionVersionsUseCase(uow)
    result, count = await uc.execute(query)
    result = [PersonalTransactionVersionSimpleResponse.from_dto(d) for d in result]
    return LimitOffsetPaginatorResult(count=count, results=result)


@transaction_router.get("/versions/{transaction_id}/{version}")
async def get_transaction_version(
    transaction_id: UUID,
    version: int,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> PersonalTransactionVersionSimpleResponse:
    query = PersonalTransactionVersionQuery(user_id, transaction_id, version)
    uc = PersonalTransactionVersionUseCase(uow)
    result = await uc.execute(query)
    return PersonalTransactionVersionSimpleResponse.from_dto(result)


@transaction_router.post("")
async def create_transaction(
    transaction: PersonalTransactionCreationRequest,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> UUID:
    command = transaction.to_command(user_id)
    uc = PersonalTransactionCreationUseCase(uow)
    dto = await uc.execute(command)
    return dto.transaction_id


@transaction_router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: UUID,
    transaction: PersonalTransactionUpdateRequest,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> None:
    command = transaction.to_command(user_id, transaction_id)
    uc = PersonalTransactionUpdateUseCase(uow)
    await uc.execute(command)


@transaction_router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> None:
    command = PersonalTransactionDeletionCommand(user_id, transaction_id)
    uc = PersonalTransactionDeletionUseCase(uow)
    await uc.execute(command)


@transaction_router.post("/{transaction_id}/restore")
async def restore_transaction(
    transaction_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> None:
    command = PersonalTransactionRestorationCommand(user_id, transaction_id)
    uc = PersonalTransactionRestorationUseCase(uow)
    await uc.execute(command)
