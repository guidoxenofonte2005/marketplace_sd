import asyncio


class LamportClock:
    def __init__(self):
        self._counter: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()

    async def tick(self) -> int:
        async with self._lock:  # não bloqueia o programa
            self._counter += 1
            return self._counter

    async def update(self, received: int) -> int:
        async with self._lock:
            self._counter = max(self._counter, received) + 1
            return self._counter
