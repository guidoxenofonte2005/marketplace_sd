# ARQUIVO TEMPORÁRIO PARA TESTES
# TODO: REFAZER ISSO TUDO E ADICIONAR O RESTO QUE PRECISA
import asyncio

from generated import notifications_pb2
from generated import notifications_pb2_grpc

import notifications.server.dispatcher
import notifications.server.idempotency
import notifications.server.lamport_clock


"""Implementação do serviço de notificações.
    Este arquivo contém:
    - EmitEvent: Recebe notificação do Marketplace
    - Subscribe: Envia notificações em streaming para o gateway"""
class NotificationServicer(notifications_pb2_grpc.NotificationServiceServicer):

    async def EmitEvent(self, request, context):
        """Recebe um evento enviado pelo Marketplace com fluxo:
        - Verifica idempotência
        - Atualiza Lamport Clock
        - Salva
        - Enfileira evento para o usuário destino"""

        event_id = request.event_id
        user_id = request.user_id
        incoming_ts = request.lamport_ts

        #Idempotência, evita duplicatas
        if await idempotency.is_already_processed(event_id):
            return notifications_pb2.EmitEventResponse(
                received=True,
                event_id=event_id
            )

        # 2. Atualização do relógio lógico
        lamport_ts = await lamport_clock.update(incoming_ts)

        #Salvar no banco (será implementado depois)
        #await db.save_event(request, lamport_ts)

        #Criar mensagem Notification
        event_message = notifications_pb2.Notification(
            event_id=event_id,
            user_id=user_id,
            message=request.message,
            lamport_ts=lamport_ts
        )

        # Enfileirar para o usuário correto
        await dispatcher.enqueue(user_id, event_message)

        # Retornar resposta para o Marketplace
        return notifications_pb2.EmitEventResponse(
            received=True,
            event_id=event_id
        )
    
    """Envia notificações ao gateway(cliente) em tempo real através 
    de streaming gRPC.Cada usuário possui sua própria fila em dispatcher."""
    async def Subscribe(self, request, context):
        user_id = request.user_id

        # Pega a fila do usuário ou cria uma se não existir
        queue = await dispatcher.get_queue(user_id)

        # Loop infinito enquanto o cliente estiver conectado
        while True:
            try:
                event = await queue.get()   # espera uma nova notificação
                yield event                 # envia para o gateway
            except asyncio.CancelledError:
                break