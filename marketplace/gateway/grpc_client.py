import grpc
from loguru import logger
from generated import marketplace_pb2_grpc
from marketplace.gateway import config as gw_config
import asyncio
from typing import Optional

class MarketplaceClient:
    def __init__(self, target: Optional[str] = None):
        self._target = target or f"{gw_config.settings.grpc_host}:{gw_config.settings.grpc_port}"
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[marketplace_pb2_grpc.MarketplaceServiceStub] = None

    async def connect(self):
        if self._channel is None:
            logger.info(f"Conectando ao Marketplace gRPC em {self._target}")
            self._channel = grpc.aio.insecure_channel(self._target)
            self._stub = marketplace_pb2_grpc.MarketplaceServiceStub(self._channel)
            try:
                await self._channel.channel_ready()
            except Exception:
                logger.warning("Canal gRPC não ficou pronto rapidamente")

    async def close(self):
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def list_products(self, request):
        await self.connect()
        return await self._stub.ListProducts(request)

    async def get_product(self, request):
        await self.connect()
        return await self._stub.GetProduct(request)

    async def place_order(self, request):
        await self.connect()
        return await self._stub.PlaceOrder(request)

    async def get_order(self, request):
        await self.connect()
        return await self._stub.GetOrder(request)

client = MarketplaceClient()