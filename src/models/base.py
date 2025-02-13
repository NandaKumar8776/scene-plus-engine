"""
Base classes for Scene+ analytics models.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import joblib
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from datetime import datetime


class ModelError(Exception):
    """Base class for model exceptions."""
    pass


class FeatureError(ModelError):
    """Raised when there's an error in feature engineering."""
    pass


class PredictionError(ModelError):
    """Raised when there's an error in making predictions."""
    pass


class BaseModel(ABC):
    """Abstract base class for all analytics models."""

    def __init__(self, model_name: str):
        """Initialize the model."""
        self.model_name = model_name
        self.model: Optional[BaseEstimator] = None
        self.feature_columns: List[str] = []
        self.target_column: Optional[str] = None
        self.last_trained: Optional[datetime] = None
        self.model_params: Dict[str, Any] = {}

    @abstractmethod
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data before training or prediction.
        
        Args:
            data: Raw input data
            
        Returns:
            DataFrame: Preprocessed data
        """
        pass

    @abstractmethod
    def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for the model.
        
        Args:
            data: Preprocessed data
            
        Returns:
            DataFrame: Data with engineered features
        """
        pass

    @abstractmethod
    def train(self, data: pd.DataFrame) -> None:
        """
        Train the model.
        
        Args:
            data: Training data
        """
        pass

    @abstractmethod
    def predict(self, data: pd.DataFrame) -> Any:
        """
        Make predictions using the trained model.
        
        Args:
            data: Data to make predictions on
            
        Returns:
            Model predictions
        """
        pass

    def save_model(self, path: str) -> None:
        """
        Save the trained model to disk.
        
        Args:
            path: Path to save the model
        """
        if self.model is None:
            raise ModelError("No trained model to save")
        
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column,
            'last_trained': self.last_trained,
            'model_params': self.model_params
        }
        
        try:
            joblib.dump(model_data, path)
        except Exception as e:
            raise ModelError(f"Failed to save model: {str(e)}")

    def load_model(self, path: str) -> None:
        """
        Load a trained model from disk.
        
        Args:
            path: Path to load the model from
        """
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.feature_columns = model_data['feature_columns']
            self.target_column = model_data['target_column']
            self.last_trained = model_data['last_trained']
            self.model_params = model_data['model_params']
        except Exception as e:
            raise ModelError(f"Failed to load model: {str(e)}")

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Get feature importance scores if available.
        
        Returns:
            Optional[DataFrame]: Feature importance scores
        """
        if self.model is None:
            raise ModelError("No trained model available")
        
        try:
            if hasattr(self.model, 'feature_importances_'):
                importance = pd.DataFrame({
                    'feature': self.feature_columns,
                    'importance': self.model.feature_importances_
                })
                return importance.sort_values('importance', ascending=False)
            return None
        except Exception as e:
            raise ModelError(f"Failed to get feature importance: {str(e)}")

    def validate_input_data(self, data: pd.DataFrame) -> None:
        """
        Validate input data format and contents.
        
        Args:
            data: Input data to validate
            
        Raises:
            FeatureError: If data validation fails
        """
        if data.empty:
            raise FeatureError("Input data is empty")
        
        missing_cols = set(self.feature_columns) - set(data.columns)
        if missing_cols:
            raise FeatureError(f"Missing required columns: {missing_cols}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information and metadata.
        
        Returns:
            Dict: Model information
        """
        return {
            'model_name': self.model_name,
            'model_type': type(self.model).__name__ if self.model else None,
            'feature_count': len(self.feature_columns),
            'features': self.feature_columns,
            'target': self.target_column,
            'last_trained': self.last_trained,
            'parameters': self.model_params
        } 