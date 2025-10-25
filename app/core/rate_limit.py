from __future__ import annotations
import time
import asyncio
from dataclasses import dataclass
from typing import Dict, Optional

from fastapi import Request, HTTPException, status
from app.core.config import get_settings


@dataclass
class Bucket:
    capacity: int
    tokens: float
    refill_rate: float
    last_refill: float


class TokenBucketRateLimiter:
    def __init__(self, rps: int, burst: int):
        self.refill_rate = float(rps)
        self.capacity = int(burst)
        self._buckets: Dict[str, Bucket] = {}
        self._lock = asyncio.Lock()

    def _now(self) -> float:
        return time.monotonic()

    def _refill(self, b: Bucket) -> None:
        now = self._now()
        elapsed = max(0.0, now - b.last_refill)
        b.tokens = min(self.capacity, b.tokens + elapsed * b.refill_rate)
        b.last_refill = now

    async def allow(self, key: str, cost: int = 1) -> bool:
        async with self._lock:
            b = self._buckets.get(key)
            if b is None:
                b = Bucket(
                    capacity=self.capacity,
                    tokens=float(self.capacity),
                    refill_rate=self.refill_rate,
                    last_refill=self._now(),
                )
                self._buckets[key] = b
            self._refill(b)
            if b.tokens >= cost:
                b.tokens -= cost
                return True
            return False


_settings_cached: Optional[tuple[int,int]] = None
_limiter: Optional[TokenBucketRateLimiter] = None


def get_limiter() -> TokenBucketRateLimiter:
    global _limiter, _settings_cached
    s = get_settings()
    conf = (s.RATE_LIMIT_RPS, s.RATE_LIMIT_BURST)
    if _limiter is None or _settings_cached != conf:
        _limiter = TokenBucketRateLimiter(
            rps=s.RATE_LIMIT_RPS,
            burst=s.RATE_LIMIT_BURST
        )
        _settings_cached = conf
    return _limiter


async def rate_limit_dependency(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    limiter = get_limiter()
    allowed = await limiter.allow(client_ip, cost=1)
    if not allowed:

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": "1"},
        )
