import grpc
from loguru import logger
from generated import marketplace_pb2_grpc
from marketplace.server.circuit_breaker import CircuitBreaker, CircuitOpenError

class MarketplaceServicer(marketplace_pb2_grpc.MarketplaceServiceServicer):
    def __init__(self, pool=None, circuit: CircuitBreaker = None):
        self.pool = pool
        self.circuit = circuit

    async def ListProducts(self, request, context):
        logger.info("[STUB] ListProducts chamado — ainda não implementado")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ListProducts ainda não implementado")
        return await super().ListProducts(request, context)

    async def GetProduct(self, request, context):
        logger.info("[STUB] GetProduct chamado — ainda não implementado")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("GetProduct ainda não implementado")
        return await super().GetProduct(request, context)

    async def PlaceOrder(self, request, context):
        # Fast-fail if circuit is open
        if self.circuit is not None and self.circuit.is_open:
            context.abort(grpc.StatusCode.UNAVAILABLE, "service unavailable (circuit open)")

        async def _do_place():
            # ... coloque aqui sua lógica real de PlaceOrder ...
            # Exemplo stub:
            logger.info("Executando PlaceOrder (stub)")
            # se for necessário acessar db use self.pool
            # raise Exception("boom")  # para testar contagem de falhas
            # retornar proto de resposta
            return await super().PlaceOrder(request, context)

        try:
            if self.circuit:
                return await self.circuit.call(lambda: _do_place())
            else:
                return await _do_place()
        except CircuitOpenError:
            context.abort(grpc.StatusCode.UNAVAILABLE, "service unavailable (circuit open)")
        except grpc.RpcError:
            # já foi tratada como grpc aborts possivelmente; re-raise
            raise
        except Exception as exc:
            logger.exception("Erro em PlaceOrder")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            # opcional: abort para interromper imediatamente
            # context.abort(grpc.StatusCode.INTERNAL, str(exc))
            # Para handlers gerados, retornar None ou chamar super:
            return await super().PlaceOrder(request, context)