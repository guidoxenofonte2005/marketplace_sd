from marketplace.server.db.queries import (
    getProductByID,
    createOrder,
    createOrderItem,
    updateStock,
)


async def placeOrder(connection, buyer_id, items):
    for item in items:
        productInfo = await getProductByID(
            connection=connection, product_id=item.product_id
        )

        if productInfo is None:
            raise ValueError("Produto não encontrado")

        if productInfo["quantity_in_stock"] < item.quantity:
            raise ValueError(f"Estoque insuficiente para produto {productInfo["name"]}")

    order = await createOrder(connection=connection, buyer_id=buyer_id)
    for item in items:
        await createOrderItem(
            connection=connection,
            order_id=order["id"],
            product_id=item.id,
            product_quantity=item.quantity,
        )
        await updateStock(
            connection=connection, product_id=item.id, product_quantity=item.quantity
        )

    return order