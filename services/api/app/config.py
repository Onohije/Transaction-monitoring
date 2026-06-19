from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://bankmon:bankmon@localhost:5432/bankmon"
    failed_tx_threshold: int = 5
    failed_tx_window_seconds: int = 300
    sim_failure_rate: float = 0.18


settings = Settings()

