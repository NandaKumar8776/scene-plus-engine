"""
Base connector interface for all data source connectors.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional

import pandas as pd
from pydantic import BaseModel


class DataSourceConfig(BaseModel):
    """Configuration for a data source."""
    name: str
    type: str
    batch_size: int = 1000
    timeout: int = 30
    connection_params: Dict[str, Any]


class BaseConnector(ABC):
    """Abstract base class for all data source connectors."""
    
    def __init__(self, config: DataSourceConfig):
        """Initialize the connector with configuration."""
        self.config = config
        self.name = config.name
        self.batch_size = config.batch_size
        self._connection = None
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the data source."""
        pass
    
    @abstractmethod
    async def fetch_batch(self, batch_size: Optional[int] = None) -> pd.DataFrame:
        """Fetch a batch of data from the source."""
        pass
    
    @abstractmethod
    async def stream_data(self) -> Generator[pd.DataFrame, None, None]:
        """Stream data from the source in batches."""
        pass
    
    async def validate_connection(self) -> bool:
        """Validate that the connection is active and working."""
        try:
            await self.connect()
            return True
        except Exception as e:
            return False
        finally:
            await self.disconnect()
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect() 