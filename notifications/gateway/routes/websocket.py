import json
import grpc

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from generated import notifications_pb2
from notifications.gateway.grpc_client import getStub
from notifications.gateway.retry import with_retry

from loguru import logger

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocketEndpoint(webSocket: WebSocket, user_id: str):
    await webSocket.accept()
    logger.info(f"Websocket aberto ao usuário {user_id}")

    try:
        stub = await getStub()
        eventStream = await with_retry(lambda: stub.Subscribe(
            notifications_pb2.SubscribeRequest(user_id=user_id)
        ))

        async for event in eventStream:
            jsonPayload = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "target_user": event.target_user,
                "payload": event.payload,
                "lamport_ts": event.lamport_ts,
                "emmited_time": event.emmited_time,
            }

            await webSocket.send_text(json.dumps(jsonPayload))
    except WebSocketDisconnect:
        logger.info(f"Websocket desconectado - Usuário {user_id}")
    except grpc.aio.AioRpcError as error:
        # caso dê algum erro de i/o no grpc
        logger.error(f"Erro no gRPC para o usuário {user_id} - {error.details}")
        await webSocket.close()
    finally:
        # fecha com segurança no final
        eventStream.close()
        logger.info(f"Stream gRPC fechado ao usuário {user_id}")
