import grpc

from fastapi import APIRouter, HTTPException
from generated import notifications_pb2
from grpc_client import stub

router = APIRouter()


@router.get("/notifications/{user_id}")
async def getHistory(user_id: str, limit: int = 10):
    try:
        response = stub.GetHistory(
            notifications_pb2.GetHistoryRequest(user_id=user_id, limit=limit)
        )

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
        if error.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404)
        raise HTTPException(status_code=500)
