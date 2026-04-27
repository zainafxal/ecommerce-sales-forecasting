from collections import defaultdict, deque
from threading import Lock
from time import time


WINDOW_SECONDS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
}


class InMemoryRateLimiter:
    def __init__(self, limit_spec: str):
        self.max_requests, self.window_seconds = self._parse_limit(limit_spec)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _parse_limit(self, limit_spec: str) -> tuple[int, int]:
        try:
            amount, window = limit_spec.strip().lower().split("/", maxsplit=1)
            max_requests = int(amount)
            normalized_window = window.rstrip("s")
            return max_requests, WINDOW_SECONDS[normalized_window]
        except (KeyError, ValueError) as exc:
            raise ValueError(
                "Invalid API_RATE_LIMIT format. Use values like '10/minute'."
            ) from exc

    def check(self, key: str) -> tuple[bool, int]:
        now = time()
        cutoff = now - self.window_seconds

        with self._lock:
            request_times = self._hits[key]

            while request_times and request_times[0] <= cutoff:
                request_times.popleft()

            if len(request_times) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (now - request_times[0])))
                return False, retry_after

            request_times.append(now)
            return True, 0
