# ARQUIVO TEMPORÁRIO PARA TESTES
import asyncio
import uuid
import grpc
from generated import notifications_pb2, notifications_pb2_grpc

async def main():
    async with grpc.aio.insecure_channel("localhost:50052") as channel:
        stub = notifications_pb2_grpc.NotificationServiceStub(channel)

        event = notifications_pb2.Event(
            event_id=str(uuid.uuid4()),
            event_type="order_confirmed",
            target_user="joao",
            payload='{"order_id": "123", "total": "R$350"}',
            lamport_ts=1,
            emmited_time=1
        )

        response = await stub.EmitEvent(event)
        print(f"Recebido: {response.received}")
        print(f"event_id: {response.event_id}")

asyncio.run(main())
