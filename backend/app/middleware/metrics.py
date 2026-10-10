import time
from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware

# Metrics definitions
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration in Seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

ACTIVE_CONNECTIONS = Gauge(
    "http_active_connections",
    "Number of active HTTP requests currently being handled"
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        endpoint = request.url.path
        method = request.method

        ACTIVE_CONNECTIONS.inc()
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            status_code = 500
            raise e
        finally:
            duration = time.time() - start_time
            ACTIVE_CONNECTIONS.dec()
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


async def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
