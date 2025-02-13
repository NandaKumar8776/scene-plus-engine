"""
Transformer for partner (Cineplex, Scotiabank) transaction data.
"""
from typing import Dict, Any
import pandas as pd

from .base import BaseTransformer, TransformationError
from ..validation.schemas import PartnerTransaction


class PartnerTransformer(BaseTransformer):
    """Transformer for partner transaction data."""

    def __init__(self):
        """Initialize partner transformer."""
        super().__init__(PartnerTransaction)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform partner transaction data into standardized format.
        
        Args:
            data: Raw partner transaction DataFrame
            
        Returns:
            DataFrame: Transformed and validated data
            
        Raises:
            TransformationError: If transformation fails
        """
        try:
            # Reset error records
            self.clear_errors()
            
            # Standardize column names
            data = data.rename(columns={
                'partner_transaction_id': 'transaction_id',
                'partner': 'partner_id',
                'scene_member_id': 'member_id',
                'timestamp': 'transaction_timestamp',
                'transaction_category': 'transaction_type',
                'transaction_amount': 'amount',
                'points_value': 'points',
                'transaction_location': 'location'
            })
            
            # Ensure datetime format
            data['transaction_timestamp'] = pd.to_datetime(data['transaction_timestamp'])
            
            # Convert numeric fields
            data['amount'] = data['amount'].astype(float)
            data['points'] = data['points'].astype(float)
            
            # Standardize partner IDs
            data['partner_id'] = data['partner_id'].str.lower()
            
            # Handle missing locations
            data['location'] = data['location'].fillna(None)
            
            # Validate each record
            validated_records = []
            for record in data.to_dict('records'):
                validated = self.validate_record(record)
                if validated:
                    validated_records.append(validated)
            
            if not validated_records:
                raise TransformationError("No valid records after transformation")
            
            return pd.DataFrame(validated_records)
            
        except Exception as e:
            raise TransformationError(f"Failed to transform partner data: {str(e)}")

    def aggregate_partner_activity(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate activity by partner and member.
        
        Args:
            data: Transformed partner transaction DataFrame
            
        Returns:
            DataFrame: Aggregated activity metrics
        """
        try:
            return data.groupby(['partner_id', 'member_id']).agg({
                'amount': 'sum',
                'points': 'sum',
                'transaction_timestamp': 'max',
                'transaction_id': 'count',
                'location': lambda x: x.value_counts().index[0] if not x.isna().all() else None
            }).rename(columns={
                'amount': 'total_spend',
                'points': 'total_points',
                'transaction_timestamp': 'last_activity',
                'transaction_id': 'transaction_count',
                'location': 'most_frequent_location'
            }).reset_index()
        except Exception as e:
            raise TransformationError(f"Failed to aggregate partner activity: {str(e)}")

    def get_partner_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate key metrics for partner transactions.
        
        Args:
            data: Transformed partner transaction DataFrame
            
        Returns:
            Dict: Dictionary containing partner metrics
        """
        try:
            metrics = {
                'total_transactions': len(data),
                'total_members': data['member_id'].nunique(),
                'total_spend': data['amount'].sum(),
                'total_points': data['points'].sum(),
                'avg_points_per_transaction': data['points'].mean(),
                'avg_spend_per_transaction': data['amount'].mean(),
                'locations_count': data['location'].nunique(),
                'transaction_types': data['transaction_type'].value_counts().to_dict()
            }
            return metrics
        except Exception as e:
            raise TransformationError(f"Failed to calculate partner metrics: {str(e)}") 