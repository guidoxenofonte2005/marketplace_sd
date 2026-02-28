# ARQUIVO TEMPORÁRIO PARA TESTES
# TODO: REFAZER ISSO TUDO E ADICIONAR O RESTO QUE PRECISA
import grpc

from loguru import logger
from generated import notifications_pb2_grpc

class NotificationServicer(notifications_pb2_grpc.NotificationServiceServicer):

    async def EmitEvent(self, request, context):
        logger.info(f"[STUB] EmitEvent chamado — ainda não implementado")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("EmitEvent ainda não implementado")
        return await super().EmitEvent(request, context)

    async def Subscribe(self, request, context):
        logger.info(f"[STUB] Subscribe chamado — ainda não implementado")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Subscribe ainda não implementado")

    async def GetHistory(self, request, context):
        logger.info(f"[STUB] GetHistory chamado — ainda não implementado")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("GetHistory ainda não implementado")
        return await super().GetHistory(request, context)
