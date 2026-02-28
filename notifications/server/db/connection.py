import asyncpg

from notifications.server.config import settings

_connectionPool: asyncpg.Pool = None


async def getConnectionPool():
    global _connectionPool
    if _connectionPool is None:
        _connectionPool = await asyncpg.create_pool(
            dsn=f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}",
            min_size=2,
            max_size=10,
        )
    return _connectionPool


async def closeConnectionPool():
    global _connectionPool
    if _connectionPool:
        await _connectionPool.close()
        _connectionPool = None
