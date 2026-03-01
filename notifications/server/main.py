"""import asyncio
import grpc

from loguru import logger

from generated import notifications_pb2_grpc
from notifications.server.config import settings
from notifications.server.db.connection import *
from notifications.server.servicer import NotificationServicer


async def serve():
    await getConnectionPool()

    server = grpc.aio.server()
    notifications_pb2_grpc.add_NotificationServiceServicer_to_server(
        servicer=NotificationServicer(), server=server
    )

    server.add_insecure_port(f"[::]:{settings.grpc_port}")
    await server.start()

    logger.info(f"Servidor rodando na porta {settings.grpc_port}")

    try:
        await server.wait_for_termination()
    finally:
        await closeConnectionPool()
        logger.info("Servidor encerrado")

if __name__ == "__main__":
    asyncio.run(serve())"""


import asyncio
import grpc
from loguru import logger

from generated import notifications_pb2_grpc
from notifications.server import discovery
from notifications.server.config import settings
#from notifications.server.db.connection import getConnectionPool, closeConnectionPool
from notifications.server.servicer import NotificationServicer, NotificationReplicationServicer


async def serve():
    """Inicializa o servidor gRPC, registra o servicer e mantém o servidor rodando.
    Também gerencia o pool de conexões do banco de dados."""

    # Inicia pool de conexões com o PostgreSQL
    logger.info("Inicializando pool de conexões com o banco")
    #await getConnectionPool()

    # Cria servidor gRPC assíncrono
    server = grpc.aio.server()

    # Registra o serviço de notificações
    notifications_pb2_grpc.add_NotificationServiceServicer_to_server(
        servicer=NotificationServicer(),
        server=server
    )

    # Registra o serviço de replicação
    notifications_pb2_grpc.add_NotificationReplicationServiceServicer_to_server(
        servicer=NotificationReplicationServicer(),
        server=server
    )

    # Porta definida no settings (ex: 50052)
    address = f"[::]:{settings.grpc_port}"
    server.add_insecure_port(address)

    # Inicia o servidor
    await server.start()
    logger.success(f"Servidor gRPC de Notificações rodando em {address}")

    await discovery.register()

    try:
        # Mantém o servidor ativo até receber SIGINT / SIGTERM
        await server.wait_for_termination()

    except Exception as e:
        logger.error(f"Erro no servidor gRPC: {e}")

    finally:
        # Fecha conexões com o banco
        logger.info("Fechando pool de conexões do banco...")
        #await closeConnectionPool()
        logger.warning("Servidor encerrado com segurança.")


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.warning("Servidor interrompido manualmente.")