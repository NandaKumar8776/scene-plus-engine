"""
Transformer for retail transaction data.
"""
from typing import Dict, Any
import pandas as pd

from .base import BaseTransformer, TransformationError
from ..validation.schemas import RetailTransaction


class RetailTransformer(BaseTransformer):
    """Transformer for retail transaction data."""

    def __init__(self):
        """Initialize retail transformer."""
        super().__init__(RetailTransaction)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform retail transaction data into standardized format.
        
        Args:
            data: Raw retail transaction DataFrame
            
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
                'trans_id': 'transaction_id',
                'store_number': 'store_id',
                'cust_id': 'customer_id',
                'timestamp': 'transaction_timestamp',
                'amount': 'total_amount',
                'retail_banner': 'banner',
                'payment_type': 'payment_method',
                'scene_points': 'points_earned'
            })
            
            # Ensure datetime format
            data['transaction_timestamp'] = pd.to_datetime(data['transaction_timestamp'])
            
            # Convert amounts to float
            data['total_amount'] = data['total_amount'].astype(float)
            data['points_earned'] = data['points_earned'].fillna(0).astype(float)
            
            # Standardize banner names
            data['banner'] = data['banner'].str.lower()
            
            # Process items column if it's in string format
            if data['items'].dtype == 'object':
                data['items'] = data['items'].apply(self._parse_items)
            
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
            raise TransformationError(f"Failed to transform retail data: {str(e)}")

    def _parse_items(self, items_str: str) -> list:
        """
        Parse items string into list of dictionaries.
        
        Args:
            items_str: String representation of items
            
        Returns:
            list: List of item dictionaries
        """
        try:
            # Handle different possible formats
            if isinstance(items_str, str):
                # If it's a string representation of a list
                if items_str.startswith('[') and items_str.endswith(']'):
                    import json
                    return json.loads(items_str)
                # If it's a pipe-separated format
                items = []
                for item_str in items_str.split('|'):
                    sku, quantity, price = item_str.split(',')
                    items.append({
                        'sku': sku.strip(),
                        'quantity': int(quantity),
                        'price': float(price)
                    })
                return items
            # If it's already a list
            elif isinstance(items_str, list):
                return items_str
            else:
                raise ValueError(f"Unsupported items format: {type(items_str)}")
        except Exception as e:
            raise TransformationError(f"Failed to parse items: {str(e)}") 