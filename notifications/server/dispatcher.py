import asyncio
from typing import Dict

# Dicionário global para armazenar as filas de eventos por usuário
_queues: Dict[str, asyncio.Queue] = {}

# O Lock impede que duas funções criem fila ao mesmo tempo
_lock = asyncio.Lock()

# Retorna a fila do usuário, se não existir, cria uma nova fila e retorna
async def get_queue(user_id: str) -> asyncio.Queue:
    async with _lock:
        if user_id not in _queues:
            _queues[user_id] = asyncio.Queue()
        return _queues[user_id]

# Coloca um evento na fila do usuário
async def enqueue(user_id: str, event):
    queue = await get_queue(user_id)
    await queue.put(event)

# Retira um item da fila do usuário e retorna, se a fila estiver vazia, 
# a função irá esperar até que um item seja adicionado
async def dequeue(user_id: str):
    queue = await get_queue(user_id)
    return await queue.get()


async def get_or_create_queue(user_id: str) -> asyncio.Queue:
    """Alias para get_queue(), apenas por legibilidade."""
    return await get_queue(user_id)