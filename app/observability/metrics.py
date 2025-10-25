from prometheus_client import Counter, Histogram, CollectorRegistry

REGISTRY = CollectorRegistry()

REQUESTS = Counter(
    "http_requests",
    "Total HTTP requests",
    ["method", "path", "status"],
    registry=REGISTRY,
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency seconds",
    buckets=(
        0.005, 0.01, 0.025, 0.05, 0.1,
        0.25, 0.5, 1.0, 2.5, 5.0, 10.0
    ),
    registry=REGISTRY,
)

EVENTS_ACCEPTED = Counter(
    "events_ingest_accepted",
    "Total accepted events",
    registry=REGISTRY,
)

EVENTS_SKIPPED = Counter(
    "events_ingest_skipped",
    "Total skipped events (duplicates/invalid)",
    registry=REGISTRY,
)
