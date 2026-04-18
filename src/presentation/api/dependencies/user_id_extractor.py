from uuid import UUID

from fastapi import HTTPException, Request, status

from infrastructure.config import FastAPISettings


async def user_id_extractor(request: Request) -> UUID:
    settings: FastAPISettings = request.app.state.fastapi_settings
    raw = request.headers.get(settings.user_id_header_name)
    if raw is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "id пользователя не передан")
    try:
        return UUID(raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "некорректный id пользователя"
        )
