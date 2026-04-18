from pydantic import BaseModel


class FastAPISettings(BaseModel):
    user_id_header_name: str = "X-User-Id"


class UvicornSettings(BaseModel):
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    loop: str = "uvloop"
