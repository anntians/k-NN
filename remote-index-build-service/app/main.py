from api.routes import build, status, cancel
from fastapi import FastAPI, Request
from core.config import Settings
from core.resources import ResourceManager
from executors.workflow_executor import WorkflowExecutor
from models.workflow import BuildWorkflow
from services.index_builder import IndexBuilder
from services.job_service import JobService
from storage.factory import RequestStoreFactory
from utils.logging_config import configure_logging
import time
from metric.BuildServiceMetrics import BuildServiceMetrics

import logging

settings = Settings()

configure_logging(settings.log_level)

logger = logging.getLogger(__name__)

request_store = RequestStoreFactory.create(
    store_type=settings.request_store_type,
    settings=settings
)

resource_manager = ResourceManager(
    total_gpu_memory=settings.gpu_memory_limit,
    total_cpu_memory=settings.cpu_memory_limit
)

index_builder = IndexBuilder(settings)

workflow_executor = WorkflowExecutor(
    max_workers=settings.max_workers,
    request_store=request_store,
    resource_manager=resource_manager,
    build_index_fn=index_builder.build_index
)

job_service = JobService(
    request_store=request_store,
    resource_manager=resource_manager,
    workflow_executor=workflow_executor,
    total_gpu_memory=settings.gpu_memory_limit,
    total_cpu_memory=settings.cpu_memory_limit
)

app = FastAPI(
    title=settings.service_name
)

app.state.job_service = job_service

metrics = BuildServiceMetrics()

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)

    path = request.url.path
    method = request.method

    status_code = response.status_code

    print("In MiddleWare")
    print(f"Request made to: {method} {path}")
    print(f"Response code {status_code}")


    end_time = time.time()
    # Track latency (Seconds)
    latency = end_time - start_time

    # Increment error counts based on status code
    if 400 <= response.status_code < 500:
        if "/build" in path:
            metrics.build_api_4xx_error_count.add(1)
        elif "/cancel" in path:
            metrics.cancel_api_4xx_error_count.add(1)
        elif "/status" in path:
            metrics.status_api_4xx_error_count.add(1)
    elif 500 <= response.status_code < 600:
        if "/build" in path:
            metrics.build_api_5xx_error_count.add(1)
        elif "/cancel" in path:
            metrics.cancel_api_5xx_error_count.add(1)
        elif "/status" in path:
            metrics.status_api_5xx_error_count.add(1)

    if "/build" in path:
        print("build api called")
        # Record latency to histogram
        metrics.build_api_latency.record(latency)
    elif "/cancel" in path:
        print("cancel api called")
        # Record latency to histogram
        metrics.cancel_api_latency.record(latency)
    elif "/status" in path:
        print("status api called")
        # Record latency to histogram
        metrics.status_api_latency.record(latency)

    return response

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application ...")
    workflow_executor.shutdown()

app.include_router(build.router)
app.include_router(status.router)
app.include_router(cancel.router)