import pydantic


class Settings(pydantic.BaseSettings):
    DEBUG: bool = False
    PROJECT_NAME: str = "undefined"
    API_STR: str = "/api"
    YANDEX_GEOCODER_API_KEY: str

    class Config:
        case_sensitive = True


settings = Settings()
