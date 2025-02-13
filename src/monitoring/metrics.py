"""
Prometheus metrics for Scene+ recommendation service.
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Dict, Any
import time

# API Metrics
REQUEST_COUNT = Counter(
    'scene_plus_request_total',
    'Total number of requests',
    ['endpoint', 'method', 'status']
)

REQUEST_LATENCY = Histogram(
    'scene_plus_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint', 'method'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Recommendation Metrics
OFFER_GENERATION_COUNT = Counter(
    'scene_plus_offers_generated_total',
    'Total number of offers generated',
    ['offer_type', 'segment']
)

OFFER_EVENTS = Counter(
    'scene_plus_offer_events_total',
    'Total number of offer events',
    ['event_type', 'offer_type']
)

OFFER_VALUE = Histogram(
    'scene_plus_offer_value',
    'Distribution of offer values',
    ['offer_type'],
    buckets=(10, 25, 50, 100, 250, 500, 1000)
)

# Customer Metrics
ACTIVE_CUSTOMERS = Gauge(
    'scene_plus_active_customers',
    'Number of active customers'
)

POINTS_BALANCE = Summary(
    'scene_plus_points_balance',
    'Distribution of customer points balances',
    ['segment']
)

# Performance Metrics
MODEL_PREDICTION_LATENCY = Histogram(
    'scene_plus_model_prediction_seconds',
    'Model prediction latency in seconds',
    ['model_name'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
)

CACHE_HITS = Counter(
    'scene_plus_cache_hits_total',
    'Total number of cache hits',
    ['cache_name']
)

CACHE_MISSES = Counter(
    'scene_plus_cache_misses_total',
    'Total number of cache misses',
    ['cache_name']
)

# Database Metrics
DB_QUERY_LATENCY = Histogram(
    'scene_plus_db_query_seconds',
    'Database query latency in seconds',
    ['operation'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

DB_CONNECTION_POOL = Gauge(
    'scene_plus_db_connections',
    'Number of database connections in the pool',
    ['state']
)


class MetricsMiddleware:
    """Middleware to collect API metrics."""
    
    def __init__(self, app):
        """Initialize middleware."""
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Process request and collect metrics."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        start_time = time.time()
        
        # Create a response interceptor
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Record request metrics
                endpoint = scope["path"]
                method = scope["method"]
                status = message["status"]
                
                REQUEST_COUNT.labels(
                    endpoint=endpoint,
                    method=method,
                    status=status
                ).inc()
                
                REQUEST_LATENCY.labels(
                    endpoint=endpoint,
                    method=method
                ).observe(time.time() - start_time)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def track_offer_generation(offer: Dict[str, Any], segment: str):
    """Track offer generation metrics."""
    OFFER_GENERATION_COUNT.labels(
        offer_type=offer['offer_type'],
        segment=segment
    ).inc()
    
    OFFER_VALUE.labels(
        offer_type=offer['offer_type']
    ).observe(offer['value'])


def track_offer_event(event_type: str, offer_type: str):
    """Track offer event metrics."""
    OFFER_EVENTS.labels(
        event_type=event_type,
        offer_type=offer_type
    ).inc()


def track_model_prediction(model_name: str, duration: float):
    """Track model prediction latency."""
    MODEL_PREDICTION_LATENCY.labels(
        model_name=model_name
    ).observe(duration)


def track_db_operation(operation: str, duration: float):
    """Track database operation latency."""
    DB_QUERY_LATENCY.labels(
        operation=operation
    ).observe(duration)


def update_customer_metrics(active_count: int, points_by_segment: Dict[str, float]):
    """Update customer-related metrics."""
    ACTIVE_CUSTOMERS.set(active_count)
    
    for segment, points in points_by_segment.items():
        POINTS_BALANCE.labels(segment=segment).observe(points)


def track_cache_operation(cache_name: str, hit: bool):
    """Track cache operations."""
    if hit:
        CACHE_HITS.labels(cache_name=cache_name).inc()
    else:
        CACHE_MISSES.labels(cache_name=cache_name).inc()


def update_db_connections(active: int, idle: int, max_connections: int):
    """Update database connection pool metrics."""
    DB_CONNECTION_POOL.labels(state="active").set(active)
    DB_CONNECTION_POOL.labels(state="idle").set(idle)
    DB_CONNECTION_POOL.labels(state="available").set(max_connections - active - idle) 