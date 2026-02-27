from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # dados do grpc
    grpc_port: int = 50051  # porta padrão
    is_primary: bool = True  # instância primária do servidor
    secondary_address: str = (
        "localhost:50052"  # endereço da instância secundária em caso de falhas
    )

    # dados do banco
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "marketplace"
    database_user: str = "marketplace_user"
    database_password: str = "marketplace_password"


settings = Settings()
