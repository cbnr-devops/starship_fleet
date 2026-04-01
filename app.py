import asyncio
import json
import logging
import os
import random
import socket
import time
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("starship_fleet")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starship_fleet starting hostname=%s", socket.gethostname())
    yield

app = FastAPI(title="Starship Fleet", lifespan=lifespan)

# --- Prometheus metrics ---
registry = CollectorRegistry(auto_describe=True)

starship_requests_counter = Counter(
    "starship_requests_total",
    "Total number of requests to the /starship endpoint",
    ["starship_name"],
    registry=registry,
)

http_request_duration = Histogram(
    "starship_fleet_http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["method", "route", "status_code"],
    buckets=[0.01, 0.05, 0.1, 0.3, 0.5, 1, 2, 5],
    registry=registry,
)

active_connections = Gauge(
    "starship_fleet_active_connections",
    "Number of active connections being handled",
    registry=registry,
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    active_connections.inc()
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    http_request_duration.labels(
        method=request.method,
        route=request.url.path,
        status_code=str(response.status_code),
    ).observe(duration)
    active_connections.dec()
    logger.info(
        "method=%s path=%s status=%s duration=%.3fs",
        request.method, request.url.path, response.status_code, duration,
    )
    return response


# --- Load static data ---
_data_path = Path(__file__).parent / "starships.json"
starships_data: list[dict] = json.loads(_data_path.read_text())


# --- Request/Response models ---
class StarshipRequest(BaseModel):
    id: int


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def index():
    html = (Path(__file__).parent / "index.html").read_text()
    return HTMLResponse(content=html)


@app.post("/starship")
async def get_starship(payload: StarshipRequest):
    start = time.time()
    await asyncio.sleep(random.uniform(1, 5))
    starship = next((s for s in starships_data if s["id"] == payload.id), None)
    duration = time.time() - start
    if starship:
        starship_requests_counter.labels(starship_name=starship["name"]).inc()
        logger.info("starship_found id=%s name=%s duration=%.3fs", payload.id, starship["name"], duration)
        return JSONResponse(content=starship)
    logger.warning("starship_not_found id=%s duration=%.3fs", payload.id, duration)
    return JSONResponse(content=None)


@app.get("/os")
async def get_os():
    return {
        "os": socket.gethostname(),
        "env": os.environ.get("NODE_ENV", os.environ.get("APP_ENV", "development")),
    }


@app.get("/live")
async def liveness():
    return {"status": "live"}


@app.get("/ready")
async def readiness():
    return {"status": "ready"}


@app.get("/metrics")
async def metrics():
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/api-docs")
async def api_docs():
    oas_path = Path(__file__).parent / "oas.json"
    if not oas_path.exists():
        return JSONResponse(status_code=404, content={"error": "OAS file not found"})
    return JSONResponse(content=json.loads(oas_path.read_text()))


# Mount static files (CSS, JS, images) after route definitions
app.mount("/", StaticFiles(directory=Path(__file__).parent), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
