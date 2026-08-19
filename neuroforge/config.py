from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    NEUROFORGE_API_KEY: str = ""
    NEUROFORGE_PROVIDER: str = "anthropic"
    NEUROFORGE_MODEL: str = "claude-sonnet-4-6"
    NEUROFORGE_MAX_TOKENS: int = 4096
    NEUROFORGE_BASE_URL: str = ""
    CHROMA_PERSIST_PATH: str = "./neuroforge-memory"
    MEMORY_VAULT_PATH: str = "./memory-vault"
    MAX_INSTANCES_PER_AGENT_TYPE: int = 3
    MEMORY_REPORT_THRESHOLD: int = 50
    MAX_TASK_RETRIES: int = 3
    LOG_LEVEL: str = "INFO"


config = Settings()
