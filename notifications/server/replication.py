import grpc
import asyncio

from generated import notifications_pb2_grpc
from notifications.server.config import settings

from loguru import logger

async def propagate(event):
    if not settings.is_primary:
        return
    
    try:
        async with grpc.aio.insecure_channel(settings.secondary_address) as channel:
            stub = notifications_pb2_grpc.NotificationReplicationServiceStub(channel=channel)
            await stub.ReplicateEvent(event)
            logger.info(f"Evento {event.event_id} replicado no servidor secundário {settings.secondary_address}")
    except Exception as e:
        logger.warning(f"Falha ao replicar evento {event.event_id}: {e}")