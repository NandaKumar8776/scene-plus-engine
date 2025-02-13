"""
Tests for customer segmentation model.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.models.customer_segmentation import CustomerSegmentation, ModelError, FeatureError


def test_model_initialization():
    """Test model initialization with default parameters."""
    model = CustomerSegmentation()
    assert model.n_clusters == 5
    assert model.model_name == "customer_segmentation"
    assert model.model is None
    assert len(model.feature_columns) > 0


def test_model_initialization_custom_clusters():
    """Test model initialization with custom number of clusters."""
    model = CustomerSegmentation(n_clusters=3)
    assert model.n_clusters == 3


def test_preprocess_data(sample_transaction_data):
    """Test data preprocessing."""
    model = CustomerSegmentation()
    processed_data = model.preprocess_data(sample_transaction_data)
    
    # Check required columns are present
    required_metrics = [
        'transaction_count',
        'last_transaction_date',
        'days_since_last_visit',
        'total_spend',
        'average_transaction_value',
        'total_points',
        'average_points_earned',
        'unique_banners',
        'average_basket_size'
    ]
    
    assert all(col in processed_data.columns for col in required_metrics)
    assert len(processed_data) > 0
    assert not processed_data.isnull().any().any()


def test_preprocess_data_missing_columns():
    """Test preprocessing with missing required columns."""
    invalid_data = pd.DataFrame({
        'customer_id': ['CUST001'],
        'total_amount': [100.0]
    })
    
    model = CustomerSegmentation()
    with pytest.raises(FeatureError):
        model.preprocess_data(invalid_data)


def test_engineer_features(sample_transaction_data):
    """Test feature engineering."""
    model = CustomerSegmentation()
    processed_data = model.preprocess_data(sample_transaction_data)
    features = model.engineer_features(processed_data)
    
    # Check all feature columns are present
    assert all(col in features.columns for col in model.feature_columns)
    
    # Check features are scaled
    assert features.mean().abs().max() < 5
    assert features.std().abs().max() < 5


def test_train_model(sample_transaction_data):
    """Test model training."""
    model = CustomerSegmentation()
    model.train(sample_transaction_data)
    
    assert model.model is not None
    assert model.last_trained is not None
    assert hasattr(model.model, 'cluster_centers_')
    assert len(model.model.cluster_centers_) == model.n_clusters


def test_predict_segments(sample_transaction_data):
    """Test segment prediction."""
    model = CustomerSegmentation()
    model.train(sample_transaction_data)
    
    segments = model.predict(sample_transaction_data)
    
    assert len(segments) == len(sample_transaction_data)
    assert 'segment' in segments.columns
    assert 'segment_description' in segments.columns
    assert segments['segment'].nunique() <= model.n_clusters


def test_predict_without_training(sample_transaction_data):
    """Test prediction without training."""
    model = CustomerSegmentation()
    with pytest.raises(ModelError):
        model.predict(sample_transaction_data)


def test_get_segment_profiles(sample_transaction_data):
    """Test getting segment profiles."""
    model = CustomerSegmentation()
    model.train(sample_transaction_data)
    
    profiles = model.get_segment_profiles()
    
    assert len(profiles) == model.n_clusters
    assert 'segment' in profiles.columns
    assert 'description' in profiles.columns
    assert all(col in profiles.columns for col in model.feature_columns)


def test_model_persistence(sample_transaction_data, tmp_path):
    """Test model saving and loading."""
    model = CustomerSegmentation()
    model.train(sample_transaction_data)
    
    # Save model
    save_path = tmp_path / "segmentation_model.joblib"
    model.save_model(str(save_path))
    
    # Load model in new instance
    new_model = CustomerSegmentation()
    new_model.load_model(str(save_path))
    
    # Compare predictions
    original_predictions = model.predict(sample_transaction_data)
    loaded_predictions = new_model.predict(sample_transaction_data)
    
    pd.testing.assert_frame_equal(original_predictions, loaded_predictions)


def test_feature_importance(sample_transaction_data):
    """Test feature importance calculation."""
    model = CustomerSegmentation()
    model.train(sample_transaction_data)
    
    importance = model.get_feature_importance()
    
    assert importance is not None
    assert len(importance) == len(model.feature_columns)
    assert 'feature' in importance.columns
    assert 'importance' in importance.columns
    assert importance['importance'].sum() > 0


def test_validate_input_data():
    """Test input data validation."""
    model = CustomerSegmentation()
    
    # Test empty DataFrame
    with pytest.raises(FeatureError):
        model.validate_input_data(pd.DataFrame())
    
    # Test missing columns
    invalid_data = pd.DataFrame({
        'invalid_column': [1, 2, 3]
    })
    with pytest.raises(FeatureError):
        model.validate_input_data(invalid_data)


def test_get_model_info(sample_transaction_data):
    """Test getting model information."""
    model = CustomerSegmentation()
    model.train(sample_transaction_data)
    
    info = model.get_model_info()
    
    assert info['model_name'] == "customer_segmentation"
    assert info['model_type'] == "KMeans"
    assert info['feature_count'] == len(model.feature_columns)
    assert info['features'] == model.feature_columns
    assert info['parameters'] == {'n_clusters': model.n_clusters}
    assert info['last_trained'] is not None 