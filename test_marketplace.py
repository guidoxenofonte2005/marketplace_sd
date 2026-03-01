# ARQUIVO TEMPORÁRIO PARA TESTES, VAI SER REFEITO DEPOIS
import asyncio
import grpc
from generated import marketplace_pb2, marketplace_pb2_grpc

async def main():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = marketplace_pb2_grpc.MarketplaceServiceStub(channel)

        # Teste 1 — ListProducts
        print("\n=== ListProducts ===")
        response = await stub.ListProducts(marketplace_pb2.ListProductsRequest())
        for p in response.product_lists:
            print(f"{p.name} — R${p.price:.2f} — Estoque: {p.quantity_in_stock}")

        # Teste 2 — GetProduct (pega o ID do primeiro produto)
        print("\n=== GetProduct ===")
        first_id = response.product_lists[0].id
        product = await stub.GetProduct(
            marketplace_pb2.GetProductRequest(product_id=first_id)
        )
        print(f"Produto: {product.name} — R${product.price:.2f}")

        # Teste 3 — PlaceOrder
        print("\n=== PlaceOrder ===")
        order = await stub.PlaceOrder(
            marketplace_pb2.PlaceOrderRequest(
                buyer_id="joao",
                ordered_items=[
                    marketplace_pb2.OrderItem(
                        product_id=first_id,
                        quantity=1
                    )
                ]
            )
        )
        print(f"Pedido criado: {order.id} — Status: {order.status}")

        # Teste 4 — GetOrder
        print("\n=== GetOrder ===")
        order_detail = await stub.GetOrder(
            marketplace_pb2.GetOrderRequest(order_id=order.id)
        )
        print(f"Pedido: {order_detail.id}")
        print(f"Comprador: {order_detail.buyer_id}")
        print(f"Status: {order_detail.status}")
        for item in order_detail.ordered_items:
            print(f"  Item: {item.product_id} — Qtd: {item.quantity}")
        
        # Teste 5 - Estoque Insuficiente
        print("\n=== Estoque insuficiente ===")
        try:
            await stub.PlaceOrder(
                marketplace_pb2.PlaceOrderRequest(
                    buyer_id="joao",
                    ordered_items=[
                        marketplace_pb2.OrderItem(
                            product_id=first_id,
                            quantity=9999
                        )
                    ]
                )
            )
        except grpc.aio.AioRpcError as e:
            print(f"Erro esperado: {e.code()} — {e.details()}")


asyncio.run(main())
