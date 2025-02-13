"""
Tests for recommendation engine.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.models.recommendation import (
    RecommendationEngine,
    Offer,
    OfferType,
    ModelError,
    FeatureError
)


def test_offer_initialization():
    """Test offer object initialization."""
    offer = Offer(
        offer_type=OfferType.POINTS_MULTIPLIER,
        value=2.0,
        conditions={'min_spend': 50.0},
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        target_banners=['Sobeys', 'Safeway']
    )
    
    assert offer.offer_type == OfferType.POINTS_MULTIPLIER
    assert offer.value == 2.0
    assert offer.conditions == {'min_spend': 50.0}
    assert isinstance(offer.start_date, datetime)
    assert isinstance(offer.end_date, datetime)
    assert offer.target_banners == ['Sobeys', 'Safeway']


def test_offer_to_dict():
    """Test offer conversion to dictionary."""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    
    offer = Offer(
        offer_type=OfferType.POINTS_BONUS,
        value=500.0,
        conditions={'min_spend': 75.0},
        start_date=start_date,
        end_date=end_date,
        target_categories=['Produce', 'Dairy']
    )
    
    offer_dict = offer.to_dict()
    
    assert offer_dict['offer_type'] == OfferType.POINTS_BONUS
    assert offer_dict['value'] == 500.0
    assert offer_dict['conditions'] == {'min_spend': 75.0}
    assert offer_dict['start_date'] == start_date.isoformat()
    assert offer_dict['end_date'] == end_date.isoformat()
    assert offer_dict['target_categories'] == ['Produce', 'Dairy']


def test_engine_initialization():
    """Test recommendation engine initialization."""
    engine = RecommendationEngine()
    
    assert engine.model_name == "recommendation_engine"
    assert isinstance(engine.scaler, object)
    assert len(engine.feature_columns) > 0


def test_preprocess_data(sample_transaction_data):
    """Test data preprocessing."""
    engine = RecommendationEngine()
    processed_data = engine.preprocess_data(sample_transaction_data)
    
    required_columns = [
        'customer_id',
        'transaction_count',
        'days_since_last_visit',
        'total_spend',
        'average_transaction',
        'total_points',
        'average_points',
        'unique_banners',
        'average_basket_size'
    ]
    
    assert all(col in processed_data.columns for col in required_columns)
    assert len(processed_data) > 0
    assert not processed_data.isnull().any().any()


def test_preprocess_data_missing_columns():
    """Test preprocessing with missing required columns."""
    invalid_data = pd.DataFrame({
        'customer_id': ['CUST001'],
        'total_amount': [100.0]
    })
    
    engine = RecommendationEngine()
    with pytest.raises(FeatureError):
        engine.preprocess_data(invalid_data)


def test_engineer_features(sample_transaction_data):
    """Test feature engineering."""
    engine = RecommendationEngine()
    processed_data = engine.preprocess_data(sample_transaction_data)
    features = engine.engineer_features(processed_data)
    
    assert all(col in features.columns for col in engine.feature_columns)
    assert features['total_spend'].between(0, 1).all()
    assert features['points_balance'].between(0, 1).all()


def test_generate_offers(sample_transaction_data, sample_customer_segments):
    """Test offer generation."""
    engine = RecommendationEngine()
    offers = engine.generate_offers(
        sample_transaction_data,
        sample_customer_segments,
        n_offers=3
    )
    
    # Check offers structure
    assert isinstance(offers, dict)
    assert len(offers) > 0
    
    # Check first customer's offers
    customer_id = list(offers.keys())[0]
    customer_offers = offers[customer_id]
    
    assert len(customer_offers) <= 3
    assert all(isinstance(offer, Offer) for offer in customer_offers)
    
    # Check offer details
    first_offer = customer_offers[0]
    assert first_offer.offer_type in [
        OfferType.POINTS_MULTIPLIER,
        OfferType.POINTS_BONUS,
        OfferType.CROSS_BANNER,
        OfferType.CATEGORY_DISCOUNT,
        OfferType.THRESHOLD_BONUS
    ]
    assert isinstance(first_offer.value, (int, float))
    assert isinstance(first_offer.conditions, dict)


def test_calculate_offer_value():
    """Test offer value calculation."""
    engine = RecommendationEngine()
    
    offer = Offer(
        offer_type=OfferType.POINTS_MULTIPLIER,
        value=2.0,
        conditions={'min_spend': 50.0},
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )
    
    customer = pd.Series({
        'average_points': 100,
        'average_transaction': 75,
        'segment_description': 'High Spender'
    })
    
    value = engine._calculate_offer_value(offer, customer)
    assert value > 0
    assert isinstance(value, float)


def test_get_recommended_banners():
    """Test banner recommendations."""
    engine = RecommendationEngine()
    customer = pd.Series({
        'banner': 'Sobeys'
    })
    
    banners = engine._get_recommended_banners(customer)
    assert isinstance(banners, list)
    assert len(banners) > 0
    assert 'Sobeys' not in banners


def test_get_recommended_categories():
    """Test category recommendations."""
    engine = RecommendationEngine()
    customer = pd.Series({})
    
    categories = engine._get_recommended_categories(customer)
    assert isinstance(categories, list)
    assert len(categories) > 0


def test_generate_offers_empty_data():
    """Test offer generation with empty data."""
    engine = RecommendationEngine()
    empty_data = pd.DataFrame()
    empty_segments = pd.DataFrame()
    
    with pytest.raises(ModelError):
        engine.generate_offers(empty_data, empty_segments)


def test_generate_offers_invalid_segments():
    """Test offer generation with invalid segment data."""
    engine = RecommendationEngine()
    
    # Create data with mismatched customer IDs
    transaction_data = pd.DataFrame({
        'customer_id': ['CUST001', 'CUST002'],
        'transaction_timestamp': [datetime.now()] * 2,
        'total_amount': [100.0, 200.0],
        'banner': ['Sobeys'] * 2,
        'points_earned': [100, 200],
        'items': [[{'sku': 'SKU001', 'quantity': 1, 'price': 100.0}]] * 2
    })
    
    segment_data = pd.DataFrame({
        'customer_id': ['CUST003', 'CUST004'],
        'segment': [0, 1]
    })
    
    with pytest.raises(ModelError):
        engine.generate_offers(transaction_data, segment_data) 