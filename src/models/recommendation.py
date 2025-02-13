"""
Recommendation engine for personalized Scene+ offers.
"""
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from .base import BaseModel, ModelError, FeatureError


class OfferType:
    """Enumeration of offer types."""
    POINTS_MULTIPLIER = "points_multiplier"
    POINTS_BONUS = "points_bonus"
    CROSS_BANNER = "cross_banner"
    CATEGORY_DISCOUNT = "category_discount"
    THRESHOLD_BONUS = "threshold_bonus"


class Offer:
    """Class representing a personalized offer."""
    
    def __init__(
        self,
        offer_type: str,
        value: float,
        conditions: Dict[str, Any],
        start_date: datetime,
        end_date: datetime,
        target_banners: Optional[List[str]] = None,
        target_categories: Optional[List[str]] = None
    ):
        self.offer_type = offer_type
        self.value = value
        self.conditions = conditions
        self.start_date = start_date
        self.end_date = end_date
        self.target_banners = target_banners
        self.target_categories = target_categories

    def to_dict(self) -> Dict[str, Any]:
        """Convert offer to dictionary format."""
        return {
            'offer_type': self.offer_type,
            'value': self.value,
            'conditions': self.conditions,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'target_banners': self.target_banners,
            'target_categories': self.target_categories
        }


class RecommendationEngine(BaseModel):
    """Engine for generating personalized offers."""

    def __init__(self):
        """Initialize recommendation engine."""
        super().__init__("recommendation_engine")
        self.scaler = MinMaxScaler()
        self.feature_columns = [
            'total_spend',
            'visit_frequency',
            'points_balance',
            'points_redemption_rate',
            'cross_banner_shopping',
            'basket_size',
            'days_since_last_visit',
            'category_diversity'
        ]

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess customer transaction data.
        
        Args:
            data: Raw customer transaction data
            
        Returns:
            DataFrame: Preprocessed data
        """
        try:
            # Validate required columns
            required_columns = [
                'customer_id', 'transaction_timestamp', 'total_amount',
                'banner', 'points_earned', 'items', 'segment'
            ]
            missing_cols = set(required_columns) - set(data.columns)
            if missing_cols:
                raise FeatureError(f"Missing required columns: {missing_cols}")

            # Calculate customer metrics
            customer_metrics = data.groupby('customer_id').agg({
                'transaction_timestamp': [
                    'count',
                    lambda x: (datetime.now() - x.max()).days
                ],
                'total_amount': ['sum', 'mean'],
                'points_earned': ['sum', 'mean'],
                'banner': 'nunique',
                'items': lambda x: np.mean([len(items) for items in x])
            }).reset_index()

            # Flatten column names
            customer_metrics.columns = [
                'customer_id', 'transaction_count', 'days_since_last_visit',
                'total_spend', 'average_transaction', 'total_points',
                'average_points', 'unique_banners', 'average_basket_size'
            ]

            return customer_metrics

        except Exception as e:
            raise FeatureError(f"Error preprocessing data: {str(e)}")

    def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for offer recommendations.
        
        Args:
            data: Preprocessed customer data
            
        Returns:
            DataFrame: Data with engineered features
        """
        try:
            features = pd.DataFrame()
            
            # Spending patterns
            features['total_spend'] = self.scaler.fit_transform(
                data[['total_spend']]
            )
            
            # Visit patterns
            features['visit_frequency'] = data['transaction_count'] / (
                data['days_since_last_visit'] + 1
            )
            
            # Points behavior
            features['points_balance'] = self.scaler.fit_transform(
                data[['total_points']]
            )
            features['points_redemption_rate'] = data['average_points'] / (
                data['average_transaction'] + 1
            )
            
            # Shopping patterns
            features['cross_banner_shopping'] = self.scaler.fit_transform(
                data[['unique_banners']]
            )
            features['basket_size'] = self.scaler.fit_transform(
                data[['average_basket_size']]
            )
            
            # Recency
            features['days_since_last_visit'] = self.scaler.fit_transform(
                data[['days_since_last_visit']]
            )
            
            # Category diversity
            features['category_diversity'] = features['cross_banner_shopping'] * features['basket_size']
            
            return features

        except Exception as e:
            raise FeatureError(f"Error engineering features: {str(e)}")

    def generate_offers(
        self,
        customer_data: pd.DataFrame,
        segment_data: pd.DataFrame,
        n_offers: int = 3
    ) -> Dict[str, List[Offer]]:
        """
        Generate personalized offers for customers.
        
        Args:
            customer_data: Customer transaction data
            segment_data: Customer segment assignments
            n_offers: Number of offers to generate per customer
            
        Returns:
            Dict: Mapping of customer IDs to list of recommended offers
        """
        try:
            # Preprocess and engineer features
            processed_data = self.preprocess_data(customer_data)
            features = self.engineer_features(processed_data)
            
            # Merge with segment data
            customer_profiles = pd.merge(
                processed_data,
                segment_data[['customer_id', 'segment', 'segment_description']],
                on='customer_id'
            )
            
            # Generate offers for each customer
            offers = {}
            for _, customer in customer_profiles.iterrows():
                offers[customer['customer_id']] = self._generate_customer_offers(
                    customer,
                    features.loc[customer.name],
                    n_offers
                )
            
            return offers

        except Exception as e:
            raise ModelError(f"Error generating offers: {str(e)}")

    def _generate_customer_offers(
        self,
        customer: pd.Series,
        features: pd.Series,
        n_offers: int
    ) -> List[Offer]:
        """Generate offers for a specific customer."""
        offers = []
        
        # Points multiplier offer
        if features['points_redemption_rate'] > 0.7:
            offers.append(Offer(
                offer_type=OfferType.POINTS_MULTIPLIER,
                value=2.0,  # 2x points
                conditions={'min_spend': 50.0},
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30)
            ))
        
        # Cross-banner offer
        if features['cross_banner_shopping'] < 0.3:
            offers.append(Offer(
                offer_type=OfferType.CROSS_BANNER,
                value=500.0,  # bonus points
                conditions={'min_spend': 75.0},
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                target_banners=self._get_recommended_banners(customer)
            ))
        
        # Category discount offer
        if features['category_diversity'] < 0.5:
            offers.append(Offer(
                offer_type=OfferType.CATEGORY_DISCOUNT,
                value=0.15,  # 15% discount
                conditions={'min_spend': 25.0},
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=14),
                target_categories=self._get_recommended_categories(customer)
            ))
        
        # Threshold bonus offer
        if features['total_spend'] > 0.7:
            offers.append(Offer(
                offer_type=OfferType.THRESHOLD_BONUS,
                value=1000.0,  # bonus points
                conditions={'spend_threshold': 150.0},
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30)
            ))
        
        # Points bonus offer
        if features['days_since_last_visit'] > 0.8:
            offers.append(Offer(
                offer_type=OfferType.POINTS_BONUS,
                value=250.0,  # bonus points
                conditions={'min_spend': 25.0},
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=7)
            ))
        
        # Sort offers by expected value and return top N
        return sorted(
            offers,
            key=lambda x: self._calculate_offer_value(x, customer),
            reverse=True
        )[:n_offers]

    def _calculate_offer_value(self, offer: Offer, customer: pd.Series) -> float:
        """Calculate expected value of an offer for a customer."""
        base_value = offer.value
        
        # Adjust value based on offer type and customer characteristics
        if offer.offer_type == OfferType.POINTS_MULTIPLIER:
            base_value *= customer['average_points']
        elif offer.offer_type == OfferType.THRESHOLD_BONUS:
            base_value *= (customer['average_transaction'] / offer.conditions['spend_threshold'])
        
        # Adjust for customer segment
        segment_multipliers = {
            'High Spender': 1.2,
            'Frequent Shopper': 1.1,
            'Points Saver': 1.3,
            'Multi-Banner': 1.15
        }
        
        multiplier = segment_multipliers.get(customer['segment_description'], 1.0)
        return base_value * multiplier

    def _get_recommended_banners(self, customer: pd.Series) -> List[str]:
        """Get recommended banners for cross-banner offers."""
        # This would typically use collaborative filtering or similar
        # For now, return a simple list
        all_banners = ['Sobeys', 'Safeway', 'IGA', 'Foodland', 'FreshCo']
        return [b for b in all_banners if b.lower() not in customer['banner'].lower()]

    def _get_recommended_categories(self, customer: pd.Series) -> List[str]:
        """Get recommended categories for category-specific offers."""
        # This would typically use collaborative filtering or similar
        # For now, return a simple list
        return ['Produce', 'Dairy', 'Meat', 'Bakery', 'Pantry']

    def train(self, data: pd.DataFrame) -> None:
        """
        Train the recommendation model (not used in basic version).
        
        Args:
            data: Training data
        """
        # In a more advanced version, this would train a collaborative filtering
        # or similar model for offer recommendations
        pass

    def predict(self, data: pd.DataFrame) -> Any:
        """
        Generate predictions (not used in basic version).
        
        Args:
            data: Input data
            
        Returns:
            Predictions
        """
        # In a more advanced version, this would generate offer recommendations
        # using a trained model
        pass 