# products queries
async def getAllProducts(connection):
    response = await connection.fetch("SELECT * FROM products")
    return response


async def getProductByID(connection, product_id):
    response = await connection.fetchrow(
        "SELECT * FROM products WHERE id = $1", product_id
    )
    return response


async def updateStock(connection, product_id, product_quantity):
    response = await connection.execute(
        "UPDATE products SET quantity_in_stock = quantity_in_stock - $1 WHERE id = $2",
        product_quantity,
        product_id,
    )
    return response


# order queries
async def createOrder(connection, buyer_id):
    response = await connection.execute(
        "INSERT INTO orders (buyer_id, status) VALUES ($1, 'pendind') RETURNING *",
        buyer_id,
    )
    return response


async def getOrderByID(connection, order_id):
    response = await connection.fetchrow("SELECT * FROM orders WHERE id = $1", order_id)
    return response


# order_items queries
async def createOrderItem(connection, order_id, product_id, product_quantity):
    response = await connection.execute(
        "INSERT INTO order_items (order_id, product_id, quantity) VALUES ($1, $2, $3)",
        order_id,
        product_id,
        product_quantity,
    )
    return response


async def getOrderItems(connection, order_id):
    response = await connection.fetch(
        "SELECT * FROM order_items WHERE order_id = $1", order_id
    )
    return response
