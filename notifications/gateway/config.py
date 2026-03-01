from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    http_port: int = 8000

    grpc_host: str = "localhost"
    grpc_port: int = 50052

settings = Settings()