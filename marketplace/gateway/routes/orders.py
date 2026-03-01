import grpc

from fastapi import APIRouter, HTTPException
from marketplace.gateway.grpc_client import client
from generated import marketplace_pb2
from marketplace.gateway.retry import with_retry

router = APIRouter()


@router.post("/orders")
async def place_order(body: dict):
    try:
        items = [
            marketplace_pb2.OrderItem(
                product_id=item["product_id"], quantity=item["quantity"]
            )
            for item in body.get("items", [])
        ]

        order = with_retry(
            lambda: client.place_order(
                marketplace_pb2.PlaceOrderRequest(
                    buyer_id=body.get("buyer_id", ""), ordered_items=items
                )
            )
        )

        return {
            "id": order.id,
            "buyer_id": order.buyer_id,
            "status": order.status,
            "items": [
                {"product_id": item.product_id, "quantity": item.quantity}
                for item in order.ordered_items
            ],
        }
    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=e.details())
        raise HTTPException(status_code=500, detail=e.details())


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    try:
        order = await with_retry(
            lambda: client.get_order(marketplace_pb2.GetOrderRequest(order_id=order_id))
        )

        return {
            "id": order.id,
            "buyer_id": order.buyer_id,
            "status": order.status,
            "items": [
                {"product_id": item.product_id, "quantity": item.quantity}
                for item in order.ordered_items
            ],
        }
    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=e.details())
        raise HTTPException(status_code=500, detail=e.details())
