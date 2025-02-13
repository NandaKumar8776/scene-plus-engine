"""
API connector for Scene+ and partner data sources.
"""
from typing import Any, Dict, Generator, Optional
import aiohttp
import pandas as pd
from datetime import datetime, timedelta

from .base import BaseConnector, DataSourceConfig


class APIConfig(DataSourceConfig):
    """API specific configuration."""
    base_url: str
    api_key: str
    api_secret: Optional[str]
    endpoints: Dict[str, str]
    headers: Optional[Dict[str, str]] = None

    class Config:
        """Pydantic config."""
        env_prefix = "API_"


class APIConnector(BaseConnector):
    """Connector for REST API data sources."""

    def __init__(self, config: APIConfig):
        """Initialize API connector."""
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            **(config.headers or {})
        }

    async def connect(self) -> None:
        """Establish API session."""
        self.session = aiohttp.ClientSession(
            base_url=self.config.base_url,
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )

    async def disconnect(self) -> None:
        """Close API session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_batch(self, batch_size: Optional[int] = None) -> pd.DataFrame:
        """Fetch a batch of data from the API."""
        size = batch_size or self.batch_size
        endpoint = self.config.endpoints.get("transactions", "")
        
        params = {
            "limit": size,
            "from_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "to_date": datetime.now().isoformat()
        }
        
        try:
            async with self.session.get(endpoint, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return pd.DataFrame(data.get("transactions", []))
        except aiohttp.ClientError as e:
            raise APIFetchError(f"Failed to fetch data from API: {str(e)}")

    async def stream_data(self) -> Generator[pd.DataFrame, None, None]:
        """Stream data from the API in batches."""
        endpoint = self.config.endpoints.get("transactions", "")
        page = 1
        
        while True:
            params = {
                "limit": self.batch_size,
                "page": page,
                "from_date": (datetime.now() - timedelta(days=7)).isoformat(),
                "to_date": datetime.now().isoformat()
            }
            
            try:
                async with self.session.get(endpoint, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    transactions = data.get("transactions", [])
                    
                    if not transactions:
                        break
                        
                    yield pd.DataFrame(transactions)
                    page += 1
            except aiohttp.ClientError as e:
                raise APIFetchError(f"Failed to stream data from API: {str(e)}")


class APIFetchError(Exception):
    """Custom exception for API fetching errors."""
    pass 