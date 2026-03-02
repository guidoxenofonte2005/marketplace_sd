import grpc
import asyncio

from generated import marketplace_pb2, marketplace_pb2_grpc
from marketplace.server.config import settings

from loguru import logger


async def replicate_order(order, items):
    try:
        orderItems = [
            marketplace_pb2.OrderItem(
                product_id=str(item["product_id"]), quantity=item["quantity"]
            )
            for item in items
        ]

        replicatedOrder = marketplace_pb2.Order(
            id=str(order["id"]),
            buyer_id=order["buyer_id"],
            ordered_items=orderItems,
            status=order["status"],
        )

        async with grpc.aio.insecure_channel(
            target=settings.secondary_address
        ) as channel:
            stub = marketplace_pb2_grpc.ReplicationServiceStub(channel=channel)
            await stub.ReplicateOrder(
                marketplace_pb2.ReplicateOrderRequest(order=replicatedOrder)
            )
            logger.info(
                f"Pedido {order["id"]} replicado para {settings.secondary_address}"
            )
    except Exception as e:
        logger.warning(f"Falha ao replicar pedido {order['id']}: {e}")


async def replicate_product(product):
    try:
        repliactionProduct = marketplace_pb2.Product(
            id=str(product["id"]),
            name=product["name"],
            description=product["description"] or "",
            price=float(product["price"]),
            quantity_in_stock=product["quantty_in_stock"],
        )

        async with grpc.aio.insecure_channel(
            target=settings.secondary_address
        ) as channel:
            stub = marketplace_pb2_grpc.ReplicationServiceStub(channel=channel)
            await stub.ReplicateOrder(
                marketplace_pb2.ReplicateProductRequest(product=repliactionProduct)
            )
            logger.info(
                f"Produto {product["id"]} replicado para {settings.secondary_address}"
            )
    except Exception as e:
        logger.warning(f"Falha ao replicar produto {product["id"]}: {e}")
