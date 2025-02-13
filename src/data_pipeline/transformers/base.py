"""
Base transformer class for data standardization.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, ValidationError

from ..validation.schemas import RetailTransaction, SceneTransaction, PartnerTransaction


class TransformerError(Exception):
    """Base class for transformer exceptions."""
    pass


class ValidationError(TransformerError):
    """Raised when data validation fails."""
    pass


class TransformationError(TransformerError):
    """Raised when data transformation fails."""
    pass


class BaseTransformer(ABC):
    """Abstract base class for data transformers."""

    def __init__(self, schema: BaseModel):
        """Initialize transformer with validation schema."""
        self.schema = schema
        self.error_records: List[Dict[str, Any]] = []

    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data into standardized format.
        
        Args:
            data: Input DataFrame to transform
            
        Returns:
            DataFrame: Transformed and validated data
            
        Raises:
            TransformationError: If transformation fails
        """
        pass

    def validate_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate a single record against the schema.
        
        Args:
            record: Dictionary containing record data
            
        Returns:
            Optional[Dict]: Validated record or None if validation fails
        """
        try:
            validated = self.schema(**record)
            return validated.dict()
        except ValidationError as e:
            self.error_records.append({
                'record': record,
                'error': str(e)
            })
            return None

    def get_error_report(self) -> pd.DataFrame:
        """
        Get report of validation errors.
        
        Returns:
            DataFrame: Error records with their validation messages
        """
        return pd.DataFrame(self.error_records)

    def clear_errors(self) -> None:
        """Clear error records."""
        self.error_records = [] 