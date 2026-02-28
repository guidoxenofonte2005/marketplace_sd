import asyncio
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
    asyncio.run(serve())
