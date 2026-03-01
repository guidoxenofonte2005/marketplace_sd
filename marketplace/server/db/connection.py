import asyncpg
from typing import Optional
from loguru import logger
from marketplace.server.config import settings

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        logger.info("Inicializando pool de conexões Postgres")
        _pool = await asyncpg.create_pool(
            dsn=f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}",
            min_size=1,
            max_size=10,
        )
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Pool de conexões fechado")
