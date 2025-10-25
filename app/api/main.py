from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog, time

from app.api.utils import extract_request_id_from_headers
from app.core.config import get_settings
from app.api.routers.ingest import router as ingest_router
from app.api.routers.stats import router as stats_router
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from app.api.middleware import PrometheusMiddleware
from app.observability.metrics import REGISTRY
from app.observability.logging import configure_json_logging


configure_json_logging()
settings = get_settings()

app = FastAPI(title="Robomate Events Analytics")

app.add_middleware(PrometheusMiddleware)


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = extract_request_id_from_headers(request.headers)
        structlog.contextvars.bind_contextvars(request_id=request_id)

        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        t0 = time.perf_counter()
        try:
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            status = response.status_code
            return response
        finally:
            dt = time.perf_counter() - t0
            structlog.contextvars.clear_contextvars()


app.add_middleware(AccessLogMiddleware)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "db": settings.POSTGRES_DB}


@app.get("/")
def healthz_empty():
    return {"status": "ok empty"}


@app.get("/metrics")
async def metrics():
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


app.include_router(ingest_router)
app.include_router(stats_router)
