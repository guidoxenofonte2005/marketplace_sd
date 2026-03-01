import uvicorn
from fastapi import FastAPI

from notifications.gateway.routes.websocket import router as socketRouter
from notifications.gateway.routes.history import router as historyRouter

from notifications.gateway.config import settings

app = FastAPI()

app.include_router(socketRouter)
app.include_router(historyRouter)

if __name__ == "__main__":
    uvicorn.run(
        "notifications.gateway.main:app",
        host="0.0.0.0",
        port=settings.http_port,
        reload=True,
    )
