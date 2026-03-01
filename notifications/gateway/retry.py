import asyncio
import grpc

from loguru import logger

MAX_RETRIES: int = 3
BASE_DELAY: float = 1.0  # segundos


async def with_retry(function):
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            return await function()
        except grpc.aio.AioRpcError as grpcError:
            retryable_errors = [
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.DEADLINE_EXCEEDED,
            ]

            if grpcError not in retryable_errors:
                pass

            last_error = grpcError
            new_delay = BASE_DELAY * (2**attempt)

            logger.warning(
                f"Tentativa {attempt + 1}/{MAX_RETRIES} falha "
                f"({grpcError.code()}). Tentando novamente em {new_delay}s"
            )

            await asyncio.sleep(new_delay)
    
    logger.error(f"Número máximo de tentativas alcançadas")
    raise last_error
