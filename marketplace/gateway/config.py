import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    http_port: int = 8001

    grpc_host: str = "localhost"
    grpc_port: int = 50051

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")

settings = Settings()