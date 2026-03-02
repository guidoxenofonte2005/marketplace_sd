import asyncio
import grpc
import json
import uuid

from generated import notifications_pb2, notifications_pb2_grpc
from marketplace.server import discovery
from marketplace.server.circuit_breaker import CircuitBreaker, CircuitOpenError

from loguru import logger

_pending_events = []
MAX_PENDING_EVENTS = 100


async def emit(
    event_type: str, payload: str, target_user: str, circuit_breaker: CircuitBreaker
):
    try:
        event = notifications_pb2.Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            target_user=target_user,
            payload=payload,
            lamport_ts=0,
            emmited_time=0,
        )

        if circuit_breaker.is_open:
            await _enqueue(event)
            return

        try:
            await circuit_breaker.call(lambda: _send(event))
            logger.info(f"Evento {event_type} emitido para {target_user}")

            await _flush_pending(circuit_breaker)
        except CircuitOpenError:
            logger.warning(f"Evento {event_type} enfileirado (circuito aberto)")
            await _enqueue(event)
        except Exception as e:
            logger.warning(f"Falha ao emitir evento {event_type} - {e}")
            await _enqueue(event)
    except Exception as e:
        logger.exception(f"Erro inesperado no emitter - {e}")


async def _send(event):
    address = await discovery.getService("notifications-service")

    async with grpc.aio.insecure_channel(target=address) as channel:
        stub = notifications_pb2_grpc.NotificationServiceStub(channel=channel)
        await stub.EmitEvent(event)


async def _enqueue(event):
    if len(_pending_events) < MAX_PENDING_EVENTS:
        _pending_events.append(event)
        logger.info(f"Evento enfileirado; Total pendente: {len(_pending_events)}")
    else:
        logger.warning(f"Fila de eventos cheia - descartando evento")


async def _flush_pending(circuit_breaker: CircuitBreaker):
    if not _pending_events:
        return
    
    pending_copy = _pending_events.copy()
    _pending_events.clear()

    for item in pending_copy:
        try:
            await circuit_breaker.call(lambda: _send(item))
            logger.info(f"Evento pendente reenviado: {item.event_id}")
        except Exception:
            await _enqueue(item)
            break
