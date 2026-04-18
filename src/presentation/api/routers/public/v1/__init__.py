from fastapi import APIRouter

from presentation.api.routers.public.v1.personal_transaction import transaction_router
from presentation.api.routers.public.v1.tenant import tenant_router
from presentation.api.routers.public.v1.transaction_category import category_router

v1_router = APIRouter(prefix="/v1", tags=["V1"])
v1_router.include_router(transaction_router)
v1_router.include_router(tenant_router)
v1_router.include_router(category_router)
