import aiohttp
from loguru import logger
from notifications.server.config import settings

CONSUL_BASE = f"http://{settings.consul_host}:{settings.consul_port}/v1"


async def register():
    payload = {
        "Name": settings.service_name,
        "Address": "172.17.0.1",
        "Port": settings.grpc_port,
        "Check": {
            "TCP": f"172.17.0.1:{settings.grpc_port}",
            "Interval": "10s",
            "DeregisterCriticalServiceAfter": "1m"
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{CONSUL_BASE}/agent/service/register",
            json=payload
        ) as response:
            if response.status == 200:
                logger.info(f"Serviço '{settings.service_name}' registrado no Consul.")
            else:
                text = await response.text()
                raise RuntimeError(f"Erro ao registrar: {response.status} — {text}")


async def get_service(name: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{CONSUL_BASE}/health/service/{name}",
            params={"passing": "true"}
        ) as response:
            if response.status != 200:
                raise RuntimeError(f"Erro ao consultar Consul: {response.status}")

            services = await response.json()

            if not services:
                raise RuntimeError(f"Nenhuma instância saudável encontrada para '{name}'")

            service = services[0]["Service"]
            address = service["Address"]
            port = service["Port"]

            logger.info(f"Serviço '{name}' descoberto em {address}:{port}")
            return f"{address}:{port}"