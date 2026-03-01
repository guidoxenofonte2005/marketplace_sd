import consul

import asyncio

if not hasattr(asyncio, "coroutine"):
    asyncio.coroutine = lambda f: f

from consul.aio import Consul
from notifications.server.config import settings
from loguru import logger


async def register() -> None:
    client = Consul(host=settings.consul_host, port=settings.consul_port)

    client.agent.service.register(
        name=settings.service_name,
        address="localhost",
        port=settings.grpc_port,
        check=consul.Check.ttl("15s"),
    )

    logger.info(f"Serviço {settings.service_name} encontrado no Consul")


async def getService(name: str) -> str:
    client = Consul(host=settings.consul_host, port=settings.consul_port)

    _, services = await client.health.service(name, passing=True)

    if not services:
        raise RuntimeError(f"Nenhuma instância de serviço encontrada para {name}")

    service = services[0]["Service"]
    service_addr = service["Address"]
    service_port = service["Port"]

    logger.info(f"Serviço {name} descoberto no endereço {service_addr}:{service_port}")
    return f"{service_addr}:{service_port}"
