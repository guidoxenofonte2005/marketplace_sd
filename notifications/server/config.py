from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # dados do grpc
    grpc_port: int = 50052
    is_primary: bool = True  # instância primária do servidor
    secondary_address: str = (
        "localhost:50053"  # endereço da instância secundária em caso de falhas
    )

    # dados do banco
    database_host: str = "localhost"
    database_port: int = 5433
    database_name: str = "notifications"
    database_user: str = "notifications_user"
    database_password: str = "notifications_password"

    # dados do consul
    consul_host: str = "localhost"
    consul_port: int = 8500
    service_name: str = "notifications-service"


settings = Settings()
