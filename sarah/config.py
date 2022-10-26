from typing import Any, Dict, Optional

import pydantic


class AsyncPostgresDsn(pydantic.PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}


class Settings(pydantic.BaseSettings):
    DEBUG: bool = False
    PROJECT_NAME: str = "undefined"
    API_STR: str = "/api"
    YANDEX_GEOCODER_API_KEY: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[pydantic.PostgresDsn] = None

    @pydantic.validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return pydantic.PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    SQLALCHEMY_DATABASE_URI_ASYNC: Optional[AsyncPostgresDsn] = None

    @pydantic.validator("SQLALCHEMY_DATABASE_URI_ASYNC", pre=True)
    def assemble_db_connection_async(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True


settings = Settings()
