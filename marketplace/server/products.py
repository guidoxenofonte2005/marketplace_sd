from marketplace.server.db.queries import getAllProducts, getProductByID


async def list_products(connection):
    return await getAllProducts(connection=connection)


async def get_product(connection, product_id):
    product = await getProductByID(connection=connection, product_id=product_id)
    if product == None:
        raise ValueError("Produto não encontrado")
    return product
