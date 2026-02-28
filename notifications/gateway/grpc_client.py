import grpc

from generated import notifications_pb2_grpc
from notifications.gateway.config import settings

_stub = None

async def getStub():
    global _stub
    if _stub is None:
        # cria canal de comunicação
        _channel = grpc.aio.insecure_channel(
            f"{settings.grpc_host}:{settings.grpc_port}"
        )

        # cria stub de notificação a partir do canal
        _stub = notifications_pb2_grpc.NotificationServiceStub(_channel)
    return _stub
