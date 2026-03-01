import asyncio
from enum import Enum
from typing import Callable, Awaitable, Optional, Any

class State(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"

class CircuitOpenError(RuntimeError):
    pass

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        check_interval: float = 5.0,
        health_check: Optional[Callable[[], Awaitable[bool]]] = None,
    ):
        self.failure_threshold = failure_threshold
        self.check_interval = check_interval
        self.health_check = health_check
        self._failures = 0
        self._state = State.CLOSED
        self._lock = asyncio.Lock()
        self._monitor_task: Optional[asyncio.Task] = None

    @property
    def failures(self) -> int:
        return self._failures

    @property
    def state(self) -> State:
        return self._state

    @property
    def is_open(self) -> bool:
        return self._state == State.OPEN

    async def _open(self) -> None:
        async with self._lock:
            if self._state == State.OPEN:
                return
            self._state = State.OPEN
            # start background monitor task (idempotent)
            if self._monitor_task is None or self._monitor_task.done():
                self._monitor_task = asyncio.create_task(self._monitor())

    async def _close(self) -> None:
        async with self._lock:
            self._failures = 0
            self._state = State.CLOSED
            if self._monitor_task is not None:
                self._monitor_task.cancel()
                self._monitor_task = None

    async def _monitor(self) -> None:
        # Periodically call health_check (if provided) until it returns True
        if self.health_check is None:
            # no health checker -> keep open indefinitely
            return
        try:
            while True:
                try:
                    ok = await self.health_check()
                except Exception:
                    ok = False
                if ok:
                    await self._close()
                    return
                await asyncio.sleep(self.check_interval)
        except asyncio.CancelledError:
            return

    async def record_success(self) -> None:
        async with self._lock:
            self._failures = 0
            if self._state == State.OPEN:
                # if already open, keep monitoring; do not auto-close here
                return

    async def record_failure(self) -> None:
        async with self._lock:
            self._failures += 1
            if self._failures >= self.failure_threshold and self._state == State.CLOSED:
                await self._open()

    async def call(self, func: Callable[[], Awaitable[Any]]) -> Any:
        """
        Wrap an async callable. Raises CircuitOpenError if circuit is open.
        On exception from func, records failure and re-raises.
        On success, records success and returns value.
        """
        if self.is_open:
            raise CircuitOpenError("circuit open")
        try:
            result = await func()
        except Exception:
            await self.record_failure()
            raise
        else:
            await self.record_success()
            return result