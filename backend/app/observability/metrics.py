"""轻量内存计数器。MVP 不接 Prometheus，先提供进程内 metrics 供 /health 与日志观测。"""

from app.core.logging import get_logger

log = get_logger("app.metrics")


class Counters:
    def __init__(self) -> None:
        self._counts: dict[str, int] = {}

    def inc(self, name: str, n: int = 1) -> None:
        self._counts[name] = self._counts.get(name, 0) + n

    def snapshot(self) -> dict[str, int]:
        return dict(self._counts)


counters = Counters()
