from uuid import UUID

from fastapi import APIRouter, Depends

from application.commands.public.tenant import (
    TenantAppointmentAdminCommand,
    TenantAppointmentAdminUseCase,
    TenantAppointmentTenantCommand,
    TenantAppointmentTenantUseCase,
)
from application.dto import LimitOffsetPaginator
from application.queries.public.tenant import (
    TenantLastVersionQuery,
    TenantLastVersionsQuery,
    TenantLastVersionsUseCase,
    TenantLastVersionUseCase,
    TenantVersionQuery,
    TenantVersionsQuery,
    TenantVersionsUseCase,
    TenantVersionUseCase,
)
from infrastructure.db.postgres import PostgresUnitOfWork
from presentation.api.dependencies import db_unit_of_work, user_id_extractor
from presentation.api.models.paginator_result import LimitOffsetPaginatorResult
from presentation.api.models.tenant import (
    TenantSimpleResponse,
    TenantVersionSimpleResponse,
)

tenant_router = APIRouter(
    prefix="/tenants",
    tags=["Tenant"],
)


@tenant_router.get("")
async def get_tenants(
    limit: int = 20,
    offset: int = 0,
    tenant_id: list[UUID] | None = None,
    status: list[str] | None = None,
    state: list[str] | None = None,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> LimitOffsetPaginatorResult[TenantSimpleResponse]:
    paginator = LimitOffsetPaginator(limit, offset)
    query = TenantLastVersionsQuery(user_id, paginator, tenant_id, status, state)
    uc = TenantLastVersionsUseCase(uow)
    result, count = await uc.execute(query)
    result = [TenantSimpleResponse.from_dto(d) for d in result]
    return LimitOffsetPaginatorResult(count=count, results=result)


@tenant_router.get("/me")
async def get_my_tenant(
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> TenantSimpleResponse:
    query = TenantLastVersionQuery(user_id, user_id)
    uc = TenantLastVersionUseCase(uow)
    dto = await uc.execute(query)
    return TenantSimpleResponse.from_dto(dto)


@tenant_router.get("/{tenant_id}")
async def get_tenant(
    tenant_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> TenantSimpleResponse:
    query = TenantLastVersionQuery(user_id, tenant_id)
    uc = TenantLastVersionUseCase(uow)
    dto = await uc.execute(query)
    return TenantSimpleResponse.from_dto(dto)


@tenant_router.get("/versions/{tenant_id}")
async def get_tenant_versions(
    tenant_id: UUID,
    limit: int = 20,
    offset: int = 0,
    status: list[str] | None = None,
    state: list[str] | None = None,
    from_version: int | None = None,
    to_version: int | None = None,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> LimitOffsetPaginatorResult[TenantVersionSimpleResponse]:
    paginator = LimitOffsetPaginator(limit, offset)
    query = TenantVersionsQuery(
        user_id,
        tenant_id,
        paginator,
        status,
        state,
        from_version,
        to_version,
    )
    uc = TenantVersionsUseCase(uow)
    result, count = await uc.execute(query)
    result = [TenantVersionSimpleResponse.from_dto(d) for d in result]
    return LimitOffsetPaginatorResult(count=count, results=result)


@tenant_router.get("/versions/{tenant_id}/{version}")
async def get_tenant_version(
    tenant_id: UUID,
    version: int,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> TenantVersionSimpleResponse:
    query = TenantVersionQuery(user_id, tenant_id, version)
    uc = TenantVersionUseCase(uow)
    dto = await uc.execute(query)
    return TenantVersionSimpleResponse.from_dto(dto)


@tenant_router.put("/{tenant_id}/appoint-admin")
async def appoint_admin(
    tenant_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> None:
    command = TenantAppointmentAdminCommand(user_id, tenant_id)
    uc = TenantAppointmentAdminUseCase(uow)
    await uc.execute(command)


@tenant_router.put("/{tenant_id}/appoint-tenant")
async def appoint_tenant(
    tenant_id: UUID,
    user_id: UUID = Depends(user_id_extractor),
    uow: PostgresUnitOfWork = Depends(db_unit_of_work),
) -> None:
    command = TenantAppointmentTenantCommand(user_id, tenant_id)
    uc = TenantAppointmentTenantUseCase(uow)
    await uc.execute(command)
