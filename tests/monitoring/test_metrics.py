"""
Tests for metrics collection module.
"""
import pytest
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.monitoring.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    OFFER_GENERATION_COUNT,
    OFFER_EVENTS,
    OFFER_VALUE,
    ACTIVE_CUSTOMERS,
    POINTS_BALANCE,
    MODEL_PREDICTION_LATENCY,
    CACHE_HITS,
    CACHE_MISSES,
    DB_QUERY_LATENCY,
    DB_CONNECTION_POOL,
    MetricsMiddleware,
    track_offer_generation,
    track_offer_event,
    track_model_prediction,
    track_db_operation,
    update_customer_metrics,
    track_cache_operation,
    update_db_connections
)


@pytest.fixture
def reset_metrics():
    """Reset all metrics before each test."""
    REQUEST_COUNT._metrics.clear()
    REQUEST_LATENCY._metrics.clear()
    OFFER_GENERATION_COUNT._metrics.clear()
    OFFER_EVENTS._metrics.clear()
    OFFER_VALUE._metrics.clear()
    ACTIVE_CUSTOMERS._metrics.clear()
    POINTS_BALANCE._metrics.clear()
    MODEL_PREDICTION_LATENCY._metrics.clear()
    CACHE_HITS._metrics.clear()
    CACHE_MISSES._metrics.clear()
    DB_QUERY_LATENCY._metrics.clear()
    DB_CONNECTION_POOL._metrics.clear()


@pytest.fixture
def mock_app():
    """Create a mock FastAPI application."""
    async def app(scope, receive, send):
        response = {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"application/json")]
        }
        await send(response)
        
        await send({
            "type": "http.response.body",
            "body": b"{}",
            "more_body": False
        })
    
    return app


@pytest.mark.asyncio
async def test_metrics_middleware(mock_app, reset_metrics):
    """Test metrics middleware."""
    middleware = MetricsMiddleware(mock_app)
    
    # Create mock scope
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test"
    }
    
    # Create mock receive
    async def receive():
        return {"type": "http.request"}
    
    # Create mock send
    responses = []
    async def send(message):
        responses.append(message)
    
    # Process request
    await middleware(scope, receive, send)
    
    # Check metrics were recorded
    assert REQUEST_COUNT._metrics
    assert REQUEST_LATENCY._metrics


def test_track_offer_generation(reset_metrics):
    """Test offer generation tracking."""
    offer = {
        'offer_type': 'points_multiplier',
        'value': 2.0
    }
    segment = 'high_value'
    
    track_offer_generation(offer, segment)
    
    assert OFFER_GENERATION_COUNT._metrics
    assert OFFER_VALUE._metrics


def test_track_offer_event(reset_metrics):
    """Test offer event tracking."""
    track_offer_event('view', 'points_multiplier')
    track_offer_event('redeem', 'points_bonus')
    
    assert OFFER_EVENTS._metrics
    assert len(OFFER_EVENTS._metrics) == 2


def test_track_model_prediction(reset_metrics):
    """Test model prediction tracking."""
    track_model_prediction('customer_segmentation', 0.1)
    
    assert MODEL_PREDICTION_LATENCY._metrics


def test_track_db_operation(reset_metrics):
    """Test database operation tracking."""
    track_db_operation('query', 0.05)
    
    assert DB_QUERY_LATENCY._metrics


def test_update_customer_metrics(reset_metrics):
    """Test customer metrics updates."""
    points_by_segment = {
        'high_value': 1000.0,
        'medium_value': 500.0,
        'low_value': 100.0
    }
    
    update_customer_metrics(100, points_by_segment)
    
    assert ACTIVE_CUSTOMERS._metrics
    assert POINTS_BALANCE._metrics


def test_track_cache_operation(reset_metrics):
    """Test cache operation tracking."""
    track_cache_operation('customer_profiles', True)
    track_cache_operation('offer_templates', False)
    
    assert CACHE_HITS._metrics
    assert CACHE_MISSES._metrics


def test_update_db_connections(reset_metrics):
    """Test database connection tracking."""
    update_db_connections(5, 10, 20)
    
    assert DB_CONNECTION_POOL._metrics


def test_request_count_labels(reset_metrics):
    """Test request count metric labels."""
    REQUEST_COUNT.labels(
        endpoint='/test',
        method='GET',
        status=200
    ).inc()
    
    REQUEST_COUNT.labels(
        endpoint='/test',
        method='POST',
        status=400
    ).inc()
    
    assert len(REQUEST_COUNT._metrics) == 2


def test_request_latency_buckets(reset_metrics):
    """Test request latency histogram buckets."""
    REQUEST_LATENCY.labels(
        endpoint='/test',
        method='GET'
    ).observe(0.1)
    
    REQUEST_LATENCY.labels(
        endpoint='/test',
        method='GET'
    ).observe(1.0)
    
    assert REQUEST_LATENCY._metrics


def test_offer_value_distribution(reset_metrics):
    """Test offer value distribution tracking."""
    values = [10, 50, 100, 500, 1000]
    for value in values:
        OFFER_VALUE.labels(
            offer_type='points_bonus'
        ).observe(value)
    
    assert OFFER_VALUE._metrics


def test_points_balance_summary(reset_metrics):
    """Test points balance summary statistics."""
    balances = [100, 500, 1000, 5000, 10000]
    for balance in balances:
        POINTS_BALANCE.labels(
            segment='high_value'
        ).observe(balance)
    
    assert POINTS_BALANCE._metrics


def test_model_prediction_latency_buckets(reset_metrics):
    """Test model prediction latency histogram buckets."""
    latencies = [0.01, 0.05, 0.1, 0.25]
    for latency in latencies:
        MODEL_PREDICTION_LATENCY.labels(
            model_name='customer_segmentation'
        ).observe(latency)
    
    assert MODEL_PREDICTION_LATENCY._metrics


def test_db_query_latency_buckets(reset_metrics):
    """Test database query latency histogram buckets."""
    latencies = [0.01, 0.05, 0.1, 0.5]
    for latency in latencies:
        DB_QUERY_LATENCY.labels(
            operation='select'
        ).observe(latency)
    
    assert DB_QUERY_LATENCY._metrics


@pytest.mark.asyncio
async def test_metrics_middleware_error_handling(mock_app, reset_metrics):
    """Test metrics middleware error handling."""
    middleware = MetricsMiddleware(mock_app)
    
    # Create scope with invalid type
    scope = {
        "type": "websocket",  # Not HTTP
        "method": "GET",
        "path": "/test"
    }
    
    async def receive():
        return {"type": "websocket.connect"}
    
    async def send(message):
        pass
    
    # Process request
    await middleware(scope, receive, send)
    
    # Check no metrics were recorded
    assert not REQUEST_COUNT._metrics
    assert not REQUEST_LATENCY._metrics 