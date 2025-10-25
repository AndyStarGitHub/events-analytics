import time
import logging
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.observability.metrics import REQUESTS, REQUEST_LATENCY


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        log = logging.getLogger("access")
        start = time.perf_counter()

        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.scope["request_id"] = request_id

        response: Response | None = None
        try:
            response = await call_next(request)

            log.info(
                f"access method={request.method} path={request.url.path} "
                f"status={response.status_code} request_id={request_id}"
            )

            response.headers["x-request-id"] = request_id
            return response

        finally:
            dur = time.perf_counter() - start
            path = request.scope.get("path", request.url.path)
            status_code = response.status_code if response is not None else 500

            REQUEST_LATENCY.observe(dur)
            REQUESTS.labels(
                method=request.method,
                path=path,
                status=str(status_code),
            ).inc()
