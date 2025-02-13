"""
Customer segmentation model using clustering techniques.
"""
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

from .base import BaseModel, ModelError, FeatureError


class CustomerSegmentation(BaseModel):
    """Customer segmentation model using K-means clustering."""

    def __init__(self, n_clusters: int = 5):
        """
        Initialize customer segmentation model.
        
        Args:
            n_clusters: Number of customer segments to create
        """
        super().__init__("customer_segmentation")
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.model_params = {'n_clusters': n_clusters}
        self.feature_columns = [
            'total_spend',
            'visit_frequency',
            'points_balance',
            'points_redemption_rate',
            'cross_banner_shopping',
            'basket_size',
            'days_since_last_visit',
            'product_categories_count'
        ]

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess customer transaction data.
        
        Args:
            data: Raw customer transaction data
            
        Returns:
            DataFrame: Preprocessed data with customer-level features
        """
        try:
            # Validate required columns
            required_columns = [
                'customer_id', 'transaction_timestamp', 'total_amount',
                'banner', 'points_earned', 'items'
            ]
            missing_cols = set(required_columns) - set(data.columns)
            if missing_cols:
                raise FeatureError(f"Missing required columns: {missing_cols}")

            # Calculate customer-level metrics
            current_date = data['transaction_timestamp'].max()
            
            customer_metrics = data.groupby('customer_id').agg({
                'transaction_timestamp': [
                    'count',
                    'max',
                    lambda x: (current_date - x.max()).days
                ],
                'total_amount': ['sum', 'mean'],
                'points_earned': ['sum', 'mean'],
                'banner': lambda x: x.nunique(),
                'items': lambda x: np.mean([len(items) for items in x])
            })

            # Flatten column names
            customer_metrics.columns = [
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

            return customer_metrics.reset_index()

        except Exception as e:
            raise FeatureError(f"Error preprocessing data: {str(e)}")

    def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for customer segmentation.
        
        Args:
            data: Preprocessed customer data
            
        Returns:
            DataFrame: Data with engineered features
        """
        try:
            features = pd.DataFrame()
            
            # Total spend
            features['total_spend'] = data['total_spend']
            
            # Visit frequency (transactions per month)
            date_range = (data['last_transaction_date'].max() - 
                        data['last_transaction_date'].min()).days / 30
            features['visit_frequency'] = data['transaction_count'] / date_range
            
            # Points metrics
            features['points_balance'] = data['total_points']
            features['points_redemption_rate'] = data['average_points_earned'] / data['average_transaction_value']
            
            # Cross-banner shopping
            features['cross_banner_shopping'] = data['unique_banners']
            
            # Basket metrics
            features['basket_size'] = data['average_basket_size']
            
            # Recency
            features['days_since_last_visit'] = data['days_since_last_visit']
            
            # Product variety
            features['product_categories_count'] = data['unique_banners'] * data['average_basket_size']
            
            # Scale features
            scaled_features = pd.DataFrame(
                self.scaler.fit_transform(features),
                columns=features.columns,
                index=features.index
            )
            
            return scaled_features

        except Exception as e:
            raise FeatureError(f"Error engineering features: {str(e)}")

    def train(self, data: pd.DataFrame) -> None:
        """
        Train the segmentation model.
        
        Args:
            data: Customer transaction data
        """
        try:
            # Preprocess data
            processed_data = self.preprocess_data(data)
            
            # Engineer features
            features = self.engineer_features(processed_data)
            
            # Initialize and train K-means model
            self.model = KMeans(
                n_clusters=self.n_clusters,
                random_state=42
            )
            
            self.model.fit(features)
            self.last_trained = datetime.now()
            
        except Exception as e:
            raise ModelError(f"Error training model: {str(e)}")

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Assign segments to customers.
        
        Args:
            data: Customer transaction data
            
        Returns:
            DataFrame: Customer segments with descriptions
        """
        try:
            # Preprocess and engineer features
            processed_data = self.preprocess_data(data)
            features = self.engineer_features(processed_data)
            
            # Predict segments
            segments = self.model.predict(features)
            
            # Create results DataFrame
            results = pd.DataFrame({
                'customer_id': processed_data['customer_id'],
                'segment': segments
            })
            
            # Add segment descriptions
            results['segment_description'] = results['segment'].map(
                self._get_segment_descriptions(features, segments)
            )
            
            return results
            
        except Exception as e:
            raise PredictionError(f"Error predicting segments: {str(e)}")

    def _get_segment_descriptions(self, features: pd.DataFrame, segments: np.ndarray) -> Dict[int, str]:
        """
        Generate descriptions for each customer segment.
        
        Args:
            features: Engineered features
            segments: Segment assignments
            
        Returns:
            Dict: Mapping of segment IDs to descriptions
        """
        # Calculate segment centers
        segment_centers = pd.DataFrame(
            self.model.cluster_centers_,
            columns=features.columns
        )
        
        descriptions = {}
        for segment_id in range(self.n_clusters):
            center = segment_centers.iloc[segment_id]
            
            # Determine key characteristics
            characteristics = []
            
            if center['total_spend'] > 0.5:
                characteristics.append("high spender")
            elif center['total_spend'] < -0.5:
                characteristics.append("low spender")
                
            if center['visit_frequency'] > 0.5:
                characteristics.append("frequent shopper")
            elif center['visit_frequency'] < -0.5:
                characteristics.append("infrequent shopper")
                
            if center['cross_banner_shopping'] > 0.5:
                characteristics.append("multi-banner")
            
            if center['points_balance'] > 0.5:
                characteristics.append("points saver")
            elif center['points_redemption_rate'] > 0.5:
                characteristics.append("points redeemer")
                
            # Create description
            description = " & ".join(characteristics) if characteristics else "average"
            descriptions[segment_id] = description.title()
            
        return descriptions

    def get_segment_profiles(self) -> pd.DataFrame:
        """
        Get detailed profiles for each segment.
        
        Returns:
            DataFrame: Segment profiles with key metrics
        """
        if self.model is None:
            raise ModelError("Model has not been trained")
            
        # Get cluster centers
        centers = pd.DataFrame(
            self.scaler.inverse_transform(self.model.cluster_centers_),
            columns=self.feature_columns
        )
        
        # Add segment descriptions
        centers['segment'] = range(self.n_clusters)
        centers['description'] = centers['segment'].map(
            self._get_segment_descriptions(
                pd.DataFrame(self.model.cluster_centers_, columns=self.feature_columns),
                range(self.n_clusters)
            )
        )
        
        return centers 