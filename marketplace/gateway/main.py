import uvicorn
from fastapi import FastAPI
from marketplace.gateway.config import settings
from marketplace.gateway.routes.products import router as products_router
from marketplace.gateway.routes.orders import router as orders_router

app = FastAPI(title="Marketplace API")

app.include_router(products_router)
app.include_router(orders_router)

if __name__ == "__main__":
    uvicorn.run(
        "marketplace.gateway.main:app",
        host="0.0.0.0",
        port=settings.http_port,
        reload=True,
    )
