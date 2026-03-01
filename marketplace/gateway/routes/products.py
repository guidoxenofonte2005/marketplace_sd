import grpc

from fastapi import APIRouter, HTTPException
from marketplace.gateway.grpc_client import client
from generated import marketplace_pb2
from marketplace.gateway.retry import with_retry

router = APIRouter()


@router.get("/products")
async def list_products():
    try:
        response = await with_retry(
            lambda: client.list_products(marketplace_pb2.ListProductsRequest())
        )

        return {
            "products": [
                {
                    "id": prod.id,
                    "name": prod.name,
                    "description": prod.description,
                    "price": prod.price,
                    "quantity_in_stock": prod.quantity_in_stock,
                }
                for prod in response.product_lists
            ]
        }
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=500, detail=e.details())


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    try:
        response = await with_retry(
            lambda: client.get_product(
                marketplace_pb2.GetProductRequest(product_id=product_id)
            )
        )

        return {
            "id": response.id,
            "name": response.name,
            "description": response.description,
            "price": response.price,
            "quantity_in_stock": response.quantity_in_stock,
        }
    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=e.details())
        raise HTTPException(status_code=500, detail=e.details())
