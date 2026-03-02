import asyncio
import json

import grpc

from loguru import logger
from generated import marketplace_pb2, marketplace_pb2_grpc

from marketplace.server.circuit_breaker import CircuitBreaker, CircuitOpenError
from marketplace.server import products, orders, event_emitter
from marketplace.server.config import settings

from marketplace.server.db import queries
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

            logger.info(
                f"Circuit Breaker — estado: {self.circuit.state}, falhas: {self.circuit.failures}"
            )

            return marketplace_pb2.ListProductsResponse(product_lists=product_list)
        except Exception as e:
            logger.exception("Erro em ListProducts")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return marketplace_pb2.ListProductsResponse()

    async def GetProduct(self, request, context):
        try:
            pool = await get_pool()
            async with pool.acquire() as connection:
                product = await products.get_product(connection, request.product_id)

            logger.info(
                f"Circuit Breaker — estado: {self.circuit.state}, falhas: {self.circuit.failures}"
            )

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
        if self.circuit.is_open:
            logger.warning("Circuito Aberto - Bloqueando PlaceOrder")
            await context.abort(
                grpc.StatusCode.UNAVAILABLE, "Serviço temporariamente indisponível"
            )

        try:
            pool = await get_pool()
            async with pool.acquire() as connection:
                order = await orders.placeOrder(
                    connection=connection,
                    buyer_id=request.buyer_id,
                    items=request.ordered_items,
                )
                orderItems = await queries.getOrderItems(
                    connection=connection, order_id=order["id"]
                )
            logger.info(
                f"Pedido {order["id"]} criado para comprador {request.buyer_id}"
            )

            from marketplace.server import event_emitter

            asyncio.create_task(
                event_emitter.emit(
                    event_type="order_confirmed",
                    payload=json.dumps({"order_id": str(order["id"])}),
                    target_user=request.buyer_id,
                    circuit_breaker=self.circuit,
                )
            )

            if settings.is_primary:
                pass

            responseItems = [
                marketplace_pb2.OrderItem(
                    product_id=str(item["product_id"]), quantity=item["quantity"]
                )
                for item in orderItems
            ]

            logger.info(
                f"Circuit Breaker — estado: {self.circuit.state}, falhas: {self.circuit.failures}"
            )

            return marketplace_pb2.Order(
                id=str(order["id"]),
                buyer_id=order["buyer_id"],
                ordered_items=responseItems,
                status=order["status"],
            )
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return marketplace_pb2.Order()
        except CircuitOpenError:
            await context.abort(
                grpc.StatusCode.UNAVAILABLE, "Serviço temporariamente indisponível"
            )
        except Exception as e:
            logger.exception("Erro em PlaceOrder")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return marketplace_pb2.Order()
        # # Fast-fail if circuit is open
        # if self.circuit is not None and self.circuit.is_open:
        #     logger.warning("Circuito Aberto - PlaceOrder bloqueado")
        #     context.abort(
        #         grpc.StatusCode.UNAVAILABLE, "service unavailable (circuit open)"
        #     )

        # async def _do_place():
        #     # ... coloque aqui sua lógica real de PlaceOrder ...
        #     # Exemplo stub:
        #     logger.info("Executando PlaceOrder (stub)")
        #     # se for necessário acessar db use self.pool
        #     # raise Exception("boom")  # para testar contagem de falhas
        #     # retornar proto de resposta
        #     return await super().PlaceOrder(request, context)

        # try:
        #     if self.circuit:
        #         return await self.circuit.call(lambda: _do_place())
        #     else:
        #         return await _do_place()
        # except CircuitOpenError:
        #     context.abort(
        #         grpc.StatusCode.UNAVAILABLE, "service unavailable (circuit open)"
        #     )
        # except grpc.RpcError:
        #     # já foi tratada como grpc aborts possivelmente; re-raise
        #     raise
        # except Exception as exc:
        #     logger.exception("Erro em PlaceOrder")
        #     context.set_code(grpc.StatusCode.INTERNAL)
        #     context.set_details(str(exc))
        #     # opcional: abort para interromper imediatamente
        #     # context.abort(grpc.StatusCode.INTERNAL, str(exc))
        #     # Para handlers gerados, retornar None ou chamar super:
        #     return await super().PlaceOrder(request, context)

    async def GetOrder(self, request, context):
        try:
            pool = await get_pool()
            async with pool.acquire() as connection:
                order = await queries.getOrderByID(
                    connection=connection, order_id=request.order_id
                )
                if order is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Pedido não encontrado")
                    return marketplace_pb2.Order()

                items = await queries.getOrderItems(
                    connection=connection, order_id=order["id"]
                )
            orderItems = [
                marketplace_pb2.OrderItem(
                    product_id=str(item["product_id"]), quantity=item["quantity"]
                )
                for item in items
            ]

            logger.info(
                f"Circuit Breaker — estado: {self.circuit.state}, falhas: {self.circuit.failures}"
            )

            return marketplace_pb2.Order(
                id=str(order["id"]),
                buyer_id=order["buyer_id"],
                ordered_items=orderItems,
                status=order["status"],
            )
        except Exception as e:
            logger.exception("Erro em GetOrder")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return marketplace_pb2.Order()
