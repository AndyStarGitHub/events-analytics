import time
from typing import Optional
from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "http_REQUESTS_TOTAL",
    "Total HTTP requests",
    labelnames=("method", "route", "status"),
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    labelnames=("route",),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

EVENTS_INGESTED = Counter(
    "events_ingested_total",
    "Events processed by /events",
    labelnames=("result",),
)

INGEST_DURATION = Histogram(
    "ingest_duration_seconds",
    "Duration of /events ingestion (seconds)",
)


class Timer:
    def __init__(self, hist: Histogram):
        self.hist = hist
        self._t0: Optional[float] = None

    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._t0 is not None:
            self.hist.observe(time.perf_counter() - self._t0)
