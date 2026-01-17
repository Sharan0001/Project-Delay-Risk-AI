"""
Prometheus Metrics for Project Delay Risk AI.

Provides observability metrics for monitoring:
- Request counts and latencies
- Analysis run counts  
- Risk level distributions
- Error rates

Usage:
    The /metrics endpoint exposes metrics in Prometheus format.
"""

import time
from functools import wraps
from typing import Callable, Any

from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess, REGISTRY
)


# =============================================================================
# Metric Definitions
# =============================================================================

# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Analysis metrics
ANALYSIS_COUNT = Counter(
    "analysis_runs_total",
    "Total number of analysis runs",
    ["what_if_scenario", "model_type"]
)

ANALYSIS_DURATION = Histogram(
    "analysis_duration_seconds",
    "Duration of analysis runs in seconds",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

TASKS_ANALYZED = Counter(
    "tasks_analyzed_total",
    "Total number of tasks analyzed",
    ["risk_level"]
)

# Current state gauges
HIGH_RISK_TASKS = Gauge(
    "high_risk_tasks_current",
    "Current number of high risk tasks from last analysis"
)

MEDIUM_RISK_TASKS = Gauge(
    "medium_risk_tasks_current",
    "Current number of medium risk tasks from last analysis"
)

LOW_RISK_TASKS = Gauge(
    "low_risk_tasks_current",
    "Current number of low risk tasks from last analysis"
)

# Error metrics
ERROR_COUNT = Counter(
    "errors_total",
    "Total number of errors",
    ["error_type"]
)


# =============================================================================
# Helper Functions
# =============================================================================

def record_request(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """Records metrics for an HTTP request."""
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code)
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


def record_analysis(
    what_if: str,
    model_type: str,
    duration: float,
    high_count: int,
    medium_count: int,
    low_count: int
) -> None:
    """Records metrics for an analysis run."""
    ANALYSIS_COUNT.labels(
        what_if_scenario=what_if or "none",
        model_type=model_type
    ).inc()
    
    ANALYSIS_DURATION.observe(duration)
    
    # Update task counters
    TASKS_ANALYZED.labels(risk_level="high").inc(high_count)
    TASKS_ANALYZED.labels(risk_level="medium").inc(medium_count)
    TASKS_ANALYZED.labels(risk_level="low").inc(low_count)
    
    # Update current state gauges
    HIGH_RISK_TASKS.set(high_count)
    MEDIUM_RISK_TASKS.set(medium_count)
    LOW_RISK_TASKS.set(low_count)


def record_error(error_type: str) -> None:
    """Records an error metric."""
    ERROR_COUNT.labels(error_type=error_type).inc()


def get_metrics() -> bytes:
    """Returns metrics in Prometheus format."""
    return generate_latest(REGISTRY)


def get_content_type() -> str:
    """Returns the content type for Prometheus metrics."""
    return CONTENT_TYPE_LATEST


# =============================================================================
# Decorators
# =============================================================================

def track_time(metric_name: str = "operation"):
    """
    Decorator to track execution time of a function.
    
    Usage:
        @track_time("my_operation")
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(
                    method="internal",
                    endpoint=metric_name
                ).observe(duration)
        return wrapper
    return decorator
