"""
Tests for Scene+ recommendation API.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from api.endpoints import app
from api.models import CustomerProfile, OfferRequest, OfferEvent


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_customer_id():
    """Get a sample customer ID."""
    return "CUST123"


@pytest.fixture
def sample_offer_id():
    """Get a sample offer ID."""
    return "OFFER123"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_get_customer_profile(client, sample_customer_id):
    """Test getting customer profile."""
    response = client.get(f"/customer/{sample_customer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == sample_customer_id
    assert "segment_id" in data
    assert "total_points" in data


def test_get_customer_profile_not_found(client):
    """Test getting non-existent customer profile."""
    response = client.get("/customer/NONEXISTENT")
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "404"


def test_generate_offers(client, sample_customer_id):
    """Test generating offers."""
    request = {
        "customer_id": sample_customer_id,
        "count": 3,
        "context": {"source": "test"}
    }
    
    response = client.post("/offers/generate", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == sample_customer_id
    assert len(data["offers"]) == 3
    assert "generated_at" in data
    
    # Check offer structure
    offer = data["offers"][0]
    assert "offer_id" in offer
    assert "offer_type" in offer
    assert "value" in offer
    assert "conditions" in offer
    assert "start_date" in offer
    assert "end_date" in offer


def test_generate_offers_invalid_count(client, sample_customer_id):
    """Test generating offers with invalid count."""
    request = {
        "customer_id": sample_customer_id,
        "count": 20,  # Too many
        "context": {}
    }
    
    response = client.post("/offers/generate", json=request)
    assert response.status_code == 422  # Validation error


def test_track_offer_event(client, sample_customer_id, sample_offer_id):
    """Test tracking offer events."""
    event = {
        "event_id": "EVENT123",
        "customer_id": sample_customer_id,
        "offer_id": sample_offer_id,
        "event_type": "view",
        "metadata": {"source": "test"}
    }
    
    response = client.post("/offers/track", json=event)
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == event["event_id"]
    assert data["customer_id"] == sample_customer_id
    assert data["offer_id"] == sample_offer_id


def test_track_offer_event_invalid_type(client, sample_customer_id, sample_offer_id):
    """Test tracking offer events with invalid type."""
    event = {
        "event_id": "EVENT123",
        "customer_id": sample_customer_id,
        "offer_id": sample_offer_id,
        "event_type": "invalid_type",
        "metadata": {}
    }
    
    response = client.post("/offers/track", json=event)
    assert response.status_code == 400
    data = response.json()
    assert "error_code" in data
    assert "valid_events" in data["message"].lower()


def test_get_offer(client, sample_offer_id):
    """Test getting offer details."""
    response = client.get(f"/offers/{sample_offer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["offer_id"] == sample_offer_id
    assert "offer_type" in data
    assert "value" in data
    assert "conditions" in data


def test_get_offer_not_found(client):
    """Test getting non-existent offer."""
    response = client.get("/offers/NONEXISTENT")
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "404"


def test_error_response_format(client):
    """Test error response format."""
    response = client.get("/nonexistent/endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data
    assert "message" in data
    assert "details" in data 