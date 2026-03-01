import asyncio

from generated import notifications_pb2
from generated import notifications_pb2_grpc

from notifications.server import dispatcher, idempotency
from notifications.server.db.connection import getConnectionPool
from notifications.server.lamport_clock import LamportClock
from notifications.server.db import queries

clock: LamportClock = LamportClock()

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

        pool = await getConnectionPool()

        async with pool.acquire() as connection:
            isAlreadyProcessed: bool = await idempotency.checkIfProcessed(
                connection=connection, event_id=request.event_id
            )
            if isAlreadyProcessed:
                # TODO: retornar EmitEventResponse(received=True, event_id=request.event_id)
                pass

            newTimestamp = await clock.update(request.lamport_ts)
            # TODO: relatório no logger dzd q o relógio tá atualizado

            await queries.saveEvent(connection=connection, event=request)

            await idempotency.markAsProcessed(
                connection=connection, event_id=request.event_id
            )

        await dispatcher.dispatch(user_id=request.targer_user, event=request)
        # TODO: logger

        return notifications_pb2.EmitEventResponse(
            received=True, event_id=request.event_id
        )

        # event_id = request.event_id
        # user_id = request.user_id
        # incoming_ts = request.lamport_ts

        # #Idempotência, evita duplicatas
        # if await idempotency.is_already_processed(event_id):
        #     return notifications_pb2.EmitEventResponse(
        #         received=True,
        #         event_id=event_id
        #     )

        # # 2. Atualização do relógio lógico
        # lamport_ts = await lamport_clock.update(incoming_ts)

        # #Salvar no banco (será implementado depois)
        # #await db.save_event(request, lamport_ts)

        # #Criar mensagem Notification
        # event_message = notifications_pb2.Notification(
        #     event_id=event_id,
        #     user_id=user_id,
        #     message=request.message,
        #     lamport_ts=lamport_ts
        # )

        # # Enfileirar para o usuário correto
        # await dispatcher.enqueue(user_id, event_message)

        # # Retornar resposta para o Marketplace
        # return notifications_pb2.EmitEventResponse(
        #     received=True,
        #     event_id=event_id
        # )

    """Envia notificações ao gateway(cliente) em tempo real através 
    de streaming gRPC.Cada usuário possui sua própria fila em dispatcher."""

    async def Subscribe(self, request, context):
        user_id = request.user_id

        # Pega a fila do usuário ou cria uma se não existir
        queue = await dispatcher.register(user_id)

        # Loop infinito enquanto o cliente estiver conectado
        try:
            while True:
                if not context.is_active():
                    break
                try:
                    event = await asyncio.wait_for(
                        queue.get(), 5.0
                    )  # espera uma nova notificação
                    await context.write(event)  # envia para o gateway
                except asyncio.TimeoutError:
                    continue
        finally:
            await dispatcher.dequeue(user_id)

    async def GetHistory(self, request, context):
        pool = await getConnectionPool()
        limit = request.limit if request.limit > 0 else 50

        async with pool.acquire() as connection:
            rows = await queries.getUserHistory(
                connection=connection, user_id=request.user_id, limit=limit
            )
        
        events = [
            notifications_pb2.Event(
                event_id=row["event_id"],
                event_type=row["event_type"],
                target_user=row["target_user"],
                payload=row["payload"] or "",
                lamport_ts=row["lamport_ts"],
                emitted_at=row["emmited_time"]
            )
            for row in rows
        ]

        return notifications_pb2.GetHistoryResponse(events=events)
