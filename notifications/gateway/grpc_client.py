import grpc

from generated import notifications_pb2_grpc
from notifications.gateway.config import settings

# cria canal de comunicação
_channel = grpc.aio.insecure_channel(f"{settings.grpc_host}:{settings.grpc_port}")

# cria stub de notificação a partir do canal
stub: notifications_pb2_grpc.NotificationServiceStub = (
    notifications_pb2_grpc.NotificationServiceStub(_channel)
)
