import os
from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import BaseModel


class EnvTypes(str, Enum):
    PROD = "prod"
    DEV = "dev"


class AppConfig(BaseModel):
    """Application configurations."""

    pass


class GlobalConfig(BaseSettings):
    """Global configurations."""

    # These variables will be loaded from the .env file. However, if
    # there is a shell environment variable having the same name,
    # that will take precedence.

    APP_CONFIG: AppConfig = AppConfig()

    # Environment specific variables do not need the field class
    SIZE_ENV_MODE: EnvTypes = EnvTypes.PROD
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "frontend.log"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "asistente-virtual-no-one"

    # API Workers, threads
    N_WORKERS: int = 1

    # Current envs
    OPENAI_API_KEY: str
    BUCKET_NAME: str
    QDRANT_URL: str
    QDRANT_KEY: str
    REDIS_HOST: str
    REDIS_PORT: int
    CHATBOT_HOST: str
    CHATBOT_PORT: int

    # Inference params
    INFERENCE_DEVICE: int = 0


env = os.getenv("SIZE_ENV_MODE", "dev")
print(f"Env: {env}")
if env == "dev":
    print("Loading Dev")
    cnf = GlobalConfig(_env_file=".dev.env")
else:
    print("Loading Prod")
    cnf = GlobalConfig(_env_file=".prod.env")
