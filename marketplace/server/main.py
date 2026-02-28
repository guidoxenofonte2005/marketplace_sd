import asyncio
import grpc
from loguru import logger

from generated import marketplace_pb2_grpc
from marketplace.server.config import settings
from marketplace.server.servicer import MarketplaceServicer
from marketplace.server.db.connection import get_pool, close_pool
from marketplace.server.circuit_breaker import CircuitBreaker

async def serve():
    pool = None
    try:
        pool = await get_pool()

        async def health_check() -> bool:
            try:
                # tenta uma query simples para validar DB/infra
                async with (await get_pool()).acquire() as conn:
                    await conn.fetchval("SELECT 1")
                return True
            except Exception:
                logger.warning("health_check falhou")
                return False

        cb = CircuitBreaker(
            failure_threshold=3,
            check_interval=getattr(settings, "circuit_check_interval", 5),
            health_check=health_check,
        )

        server = grpc.aio.server()
        marketplace_pb2_grpc.add_MarketplaceServiceServicer_to_server(
            MarketplaceServicer(pool=pool, circuit=cb), server
        )
        server.add_insecure_port(f"[::]:{settings.grpc_port}")
        await server.start()
        logger.info(f"Marketplace gRPC rodando na porta {settings.grpc_port}")
        await server.wait_for_termination()
    finally:
        if pool is not None:
            await close_pool()
        logger.info("Marketplace server finalizado")

if __name__ == "__main__":
    asyncio.run(serve())