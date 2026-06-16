from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    debug: bool = True

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "db"
    postgres_port: int = 5432

    def _build_postgres_url(self, driver: str) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=f"postgresql+{driver}",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @property
    def database_url(self) -> PostgresDsn:
        return self._build_postgres_url("asyncpg")

    @property
    def sync_database_url(self) -> PostgresDsn:
        return self._build_postgres_url("psycopg")


settings = Settings()
