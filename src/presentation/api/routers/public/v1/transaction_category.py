from uuid import UUID

from fastapi import APIRouter, Depends

from application.commands.public.transaction_category import (
    TransactionCategoryCreationUseCase,
    TransactionCategoryDeletionCommand,
    TransactionCategoryDeletionUseCase,
    TransactionCategoryRestorationCommand,
    TransactionCategoryRestorationUseCase,
    TransactionCategoryUpdateUseCase,
)
from application.dto import LimitOffsetPaginator
from application.queries.public.transaction_category import (
    TransactionCategoryLastVersionQuery,
    TransactionCategoryLastVersionsQuery,
    TransactionCategoryLastVersionsUseCase,
    TransactionCategoryLastVersionUseCase,
    TransactionCategoryVersionQuery,
    TransactionCategoryVersionsQuery,
    TransactionCategoryVersionsUseCase,
    TransactionCategoryVersionUseCase,
)
from infrastructure.db.postgres import PostgresUnitOfWork
from presentation.api.dependencies import db_unit_of_work, user_id_extractor
from presentation.api.models.paginator_result import LimitOffsetPaginatorResult
from presentation.api.models.transaction_category import (
    TransactionCategoryCreationRequest,
    TransactionCategorySimpleResponse,
    TransactionCategoryUpdateRequest,
    TransactionCategoryVersionSimpleResponse,
)

category_router = APIRouter(
    prefix="/transaction-categories",
    tags=["Transaction category"],
)


@category_router.get("")
async def get_categories(
    limit: int = 20,
    offset: int = 0,
    category_id: list[UUID] | None = None,
    name: list[str] | None = None,
    state: list[str] | None = None,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> LimitOffsetPaginatorResult[TransactionCategorySimpleResponse]:
    paginator = LimitOffsetPaginator(limit, offset)
    query = TransactionCategoryLastVersionsQuery(
        user_id, paginator, category_id, name, state
    )
    uc = TransactionCategoryLastVersionsUseCase(uow)
    result, count = await uc.execute(query)
    result = [TransactionCategorySimpleResponse.from_dto(d) for d in result]
    return LimitOffsetPaginatorResult(count=count, results=result)


@category_router.get("/{category_id}")
async def get_transaction(
    category_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> TransactionCategorySimpleResponse:
    query = TransactionCategoryLastVersionQuery(user_id, category_id)
    uc = TransactionCategoryLastVersionUseCase(uow)
    result = await uc.execute(query)
    return TransactionCategorySimpleResponse.from_dto(result)


@category_router.get("/versions/{category_id}")
async def get_transactions_versions(
    category_id: UUID,
    limit: int = 20,
    offset: int = 0,
    name: list[str] | None = None,
    state: list[str] | None = None,
    from_version: int | None = None,
    to_version: int | None = None,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> LimitOffsetPaginatorResult[TransactionCategoryVersionSimpleResponse]:
    paginator = LimitOffsetPaginator(limit, offset)
    query = TransactionCategoryVersionsQuery(
        user_id,
        paginator,
        category_id,
        name,
        state,
        from_version,
        to_version,
    )
    uc = TransactionCategoryVersionsUseCase(uow)
    result, count = await uc.execute(query)
    result = [TransactionCategoryVersionSimpleResponse.from_dto(d) for d in result]
    return LimitOffsetPaginatorResult(count=count, results=result)


@category_router.get("/versions/{category_id}/{version}")
async def get_transaction_version(
    category_id: UUID,
    version: int,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> TransactionCategoryVersionSimpleResponse:
    query = TransactionCategoryVersionQuery(user_id, category_id, version)
    uc = TransactionCategoryVersionUseCase(uow)
    result = await uc.execute(query)
    return TransactionCategoryVersionSimpleResponse.from_dto(result)


@category_router.post("")
async def create_transaction(
    category: TransactionCategoryCreationRequest,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> UUID:
    command = category.to_command(user_id)
    uc = TransactionCategoryCreationUseCase(uow)
    dto = await uc.execute(command)
    return dto.category_id


@category_router.put("/{category_id}")
async def update_transaction(
    category_id: UUID,
    category: TransactionCategoryUpdateRequest,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> None:
    command = category.to_command(user_id, category_id)
    uc = TransactionCategoryUpdateUseCase(uow)
    await uc.execute(command)


@category_router.delete("/{category_id}")
async def delete_transaction(
    category_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> None:
    command = TransactionCategoryDeletionCommand(user_id, category_id)
    uc = TransactionCategoryDeletionUseCase(uow)
    await uc.execute(command)


@category_router.post("/{category_id}/restore")
async def restore_transaction(
    category_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> None:
    command = TransactionCategoryRestorationCommand(user_id, category_id)
    uc = TransactionCategoryRestorationUseCase(uow)
    await uc.execute(command)
