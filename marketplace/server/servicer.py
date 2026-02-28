import grpc

from loguru import logger
from generated import marketplace_pb2, marketplace_pb2_grpc
from marketplace.server.circuit_breaker import CircuitBreaker, CircuitOpenError

from marketplace.server import products, orders, event_emitter

from marketplace.server.db.connection import get_pool


class MarketplaceServicer(marketplace_pb2_grpc.MarketplaceServiceServicer):
    def __init__(self, circuit: CircuitBreaker = None):
        # self.pool = pool
        self.circuit = circuit

    async def ListProducts(self, request, context):
        # logger.info("[STUB] ListProducts chamado — ainda não implementado")
        # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        # context.set_details("ListProducts ainda não implementado")
        # return await super().ListProducts(request, context)
        try:
            pool = await get_pool()

            async with pool.acquire() as connection:
                rows = await products.list_products(connection)

            product_list = [
                marketplace_pb2.Product(
                    id=str(row["id"]),
                    name=row["name"],
                    description=row["description"] or "",
                    price=float(row["price"]),
                    quantity_in_stock=row["quantity_in_stock"],
                )
                for row in rows
            ]

            return marketplace_pb2.ListProductsResponse(product_lists=product_list)
        except Exception as e:
            logger.exception("Erro em ListProducts")
            context.send_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return marketplace_pb2.ListProductsResponse()

    async def GetProduct(self, request, context):
        try:
            pool = await get_pool()
            async with pool.acquire() as connection:
                product = await products.get_product(connection, request.product_id)

            return marketplace_pb2.Product(
                id=str(product["id"]),
                name=product["name"],
                description=product["description"] or "",
                price=float(product["price"]),
                quantity_in_stock=product["quantity_in_stock"],
            )
        except ValueError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return marketplace_pb2.Product()
        except Exception as e:
            logger.exception("Erro em GetProduct")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return marketplace_pb2.Product()

    async def PlaceOrder(self, request, context):
        # Fast-fail if circuit is open
        if self.circuit is not None and self.circuit.is_open:
            logger.warning("Circuito Aberto - PlaceOrder bloqueado")
            context.abort(
                grpc.StatusCode.UNAVAILABLE, "service unavailable (circuit open)"
            )

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
            context.abort(
                grpc.StatusCode.UNAVAILABLE, "service unavailable (circuit open)"
            )
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
