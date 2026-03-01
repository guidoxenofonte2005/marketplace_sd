import grpc

import traceback

from fastapi import APIRouter, HTTPException
from generated import notifications_pb2
from notifications.gateway.grpc_client import getStub
from notifications.gateway.retry import with_retry

from loguru import logger

router = APIRouter()


@router.get("/notifications/{user_id}")
async def getHistory(user_id: str, limit: int = 10):
    try:
        stub = await getStub()
        response = await with_retry(lambda: stub.GetHistory(
            notifications_pb2.GetHistoryRequest(user_id=user_id, limit=limit)
        ))

        events = [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "target_user": event.target_user,
                "payload": event.payload,
                "lamport_ts": event.lamport_ts,
                "emmited_time": event.emmited_time,
            }
            for event in response.events
        ]

        return {"user_id": user_id, "events": events}
    except grpc.aio.AioRpcError as error:
        logger.error(f"Erro ao buscar histório: {error}")
        logger.error(traceback.format_exc())
        if error.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404)
        raise HTTPException(status_code=500)
