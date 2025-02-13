"""
Pytest configuration and shared fixtures.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

from src.models.customer_segmentation import CustomerSegmentation
from src.models.recommendation import RecommendationEngine, Offer


@pytest.fixture
def sample_transaction_data() -> pd.DataFrame:
    """Generate sample transaction data for testing."""
    np.random.seed(42)
    
    # Generate 100 sample transactions
    n_samples = 100
    
    data = {
        'customer_id': [f'CUST{i:03d}' for i in np.random.randint(1, 21, n_samples)],
        'transaction_timestamp': [
            datetime.now() - timedelta(days=np.random.randint(0, 30))
            for _ in range(n_samples)
        ],
        'total_amount': np.random.uniform(10, 200, n_samples),
        'banner': np.random.choice(['Sobeys', 'Safeway', 'IGA', 'Foodland'], n_samples),
        'points_earned': np.random.uniform(10, 1000, n_samples),
        'items': [
            [
                {
                    'sku': f'SKU{i:03d}',
                    'quantity': np.random.randint(1, 5),
                    'price': np.random.uniform(5, 50)
                }
                for i in range(np.random.randint(1, 6))
            ]
            for _ in range(n_samples)
        ]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_customer_segments(sample_transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Generate sample customer segments."""
    # Initialize and train segmentation model
    model = CustomerSegmentation(n_clusters=5)
    model.train(sample_transaction_data)
    
    # Get segments
    return model.predict(sample_transaction_data)


@pytest.fixture
def sample_offer_events() -> pd.DataFrame:
    """Generate sample offer events for testing."""
    np.random.seed(42)
    
    # Generate 100 sample events
    n_samples = 100
    
    data = {
        'event_id': [f'EVENT{i:03d}' for i in range(n_samples)],
        'customer_id': [f'CUST{i:03d}' for i in np.random.randint(1, 21, n_samples)],
        'offer_id': [f'OFFER{i:03d}' for i in range(n_samples)],
        'event_type': np.random.choice(['generate', 'view', 'click', 'redeem'], n_samples),
        'offer_type': np.random.choice([
            'points_multiplier', 'points_bonus', 'cross_banner',
            'category_discount', 'threshold_bonus'
        ], n_samples),
        'offer_value': np.random.uniform(10, 1000, n_samples),
        'timestamp': [
            datetime.now() - timedelta(days=np.random.randint(0, 30))
            for _ in range(n_samples)
        ]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_api_metrics() -> pd.DataFrame:
    """Generate sample API metrics for testing."""
    np.random.seed(42)
    
    # Generate 1000 sample requests
    n_samples = 1000
    
    data = {
        'timestamp': [
            datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            for _ in range(n_samples)
        ],
        'endpoint': np.random.choice([
            '/customer/{id}',
            '/offers/generate',
            '/offers/track',
            '/offers/{id}'
        ], n_samples),
        'method': np.random.choice(['GET', 'POST'], n_samples),
        'status': np.random.choice([200, 201, 400, 404, 500], n_samples, p=[0.8, 0.1, 0.05, 0.03, 0.02]),
        'latency': np.random.exponential(0.1, n_samples)
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_model_metrics() -> pd.DataFrame:
    """Generate sample model prediction metrics."""
    np.random.seed(42)
    
    # Generate 500 sample predictions
    n_samples = 500
    
    data = {
        'timestamp': [
            datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            for _ in range(n_samples)
        ],
        'model_name': np.random.choice([
            'customer_segmentation',
            'recommendation_engine'
        ], n_samples),
        'latency': np.random.exponential(0.05, n_samples),
        'prediction_id': [f'PRED{i:03d}' for i in range(n_samples)]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def recommendation_engine() -> RecommendationEngine:
    """Create a recommendation engine instance for testing."""
    return RecommendationEngine()


@pytest.fixture
def segmentation_model() -> CustomerSegmentation:
    """Create a customer segmentation model instance for testing."""
    return CustomerSegmentation(n_clusters=5)


@pytest.fixture
def mock_db_session(monkeypatch):
    """Mock database session for testing."""
    class MockDBSession:
        def __init__(self):
            self.committed = False
            self.rolled_back = False
            self.closed = False
            self.queries = []
        
        def commit(self):
            self.committed = True
        
        def rollback(self):
            self.rolled_back = True
        
        def close(self):
            self.closed = True
        
        def execute(self, query, params=None):
            self.queries.append((query, params))
            return self
        
        def fetchall(self):
            return []
        
        def fetchone(self):
            return None
    
    session = MockDBSession()
    monkeypatch.setattr("src.data_pipeline.db.Session", lambda: session)
    return session 