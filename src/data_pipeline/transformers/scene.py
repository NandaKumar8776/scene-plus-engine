"""
Transformer for Scene+ transaction data.
"""
from typing import Dict, Any
import pandas as pd

from .base import BaseTransformer, TransformationError
from ..validation.schemas import SceneTransaction


class SceneTransformer(BaseTransformer):
    """Transformer for Scene+ transaction data."""

    def __init__(self):
        """Initialize Scene+ transformer."""
        super().__init__(SceneTransaction)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform Scene+ transaction data into standardized format.
        
        Args:
            data: Raw Scene+ transaction DataFrame
            
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
                'scene_transaction_id': 'transaction_id',
                'scene_member_id': 'member_id',
                'type': 'transaction_type',
                'points_value': 'points',
                'timestamp': 'transaction_timestamp',
                'partner_name': 'partner',
                'original_transaction_id': 'source_transaction_id'
            })
            
            # Ensure datetime format
            data['transaction_timestamp'] = pd.to_datetime(data['transaction_timestamp'])
            
            # Convert points to float
            data['points'] = data['points'].astype(float)
            
            # Standardize transaction types
            data['transaction_type'] = data['transaction_type'].str.lower()
            
            # Standardize partner names
            data['partner'] = data['partner'].str.lower()
            
            # Handle missing source transaction IDs
            data['source_transaction_id'] = data['source_transaction_id'].fillna(None)
            
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
            raise TransformationError(f"Failed to transform Scene+ data: {str(e)}")

    def aggregate_member_points(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate points by member.
        
        Args:
            data: Transformed Scene+ transaction DataFrame
            
        Returns:
            DataFrame: Aggregated points by member
        """
        try:
            return data.groupby('member_id').agg({
                'points': lambda x: sum(x * (x.index.get_level_values('transaction_type') == 'earn') - 
                                     x * (x.index.get_level_values('transaction_type') == 'redeem')),
                'transaction_timestamp': 'max',
                'transaction_id': 'count'
            }).rename(columns={
                'points': 'total_points',
                'transaction_timestamp': 'last_activity',
                'transaction_id': 'transaction_count'
            }).reset_index()
        except Exception as e:
            raise TransformationError(f"Failed to aggregate member points: {str(e)}") 