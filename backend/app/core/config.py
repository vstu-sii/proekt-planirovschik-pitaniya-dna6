import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://meal_planner:meal_planner@localhost:5432/meal_planner",
    )
    ai_provider: str = os.getenv("AI_PROVIDER", "demo")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://llm-mock:8080")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    trace_collector_url: str = os.getenv("TRACE_COLLECTOR_URL", "")
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:8080,http://localhost:8081"
        ).split(",")
        if origin.strip()
    )


settings = Settings()
