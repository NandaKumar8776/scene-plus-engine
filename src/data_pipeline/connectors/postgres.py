"""
PostgreSQL connector for retail transaction data.
"""
from typing import Any, Dict, Generator, Optional

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .base import BaseConnector, DataSourceConfig


class PostgresConfig(DataSourceConfig):
    """PostgreSQL specific configuration."""
    host: str
    port: int
    database: str
    user: str
    password: str
    schema: str = "public"

    class Config:
        """Pydantic config."""
        env_prefix = "DB_"


class PostgresConnector(BaseConnector):
    """Connector for PostgreSQL databases."""

    def __init__(self, config: PostgresConfig):
        """Initialize PostgreSQL connector."""
        super().__init__(config)
        self.engine: Optional[Engine] = None
        self._connection_string = (
            f"postgresql://{config.user}:{config.password}@"
            f"{config.host}:{config.port}/{config.database}"
        )

    async def connect(self) -> None:
        """Establish connection to PostgreSQL database."""
        try:
            self.engine = create_engine(self._connection_string)
            self._connection = self.engine.connect()
        except SQLAlchemyError as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")

    async def disconnect(self) -> None:
        """Close the PostgreSQL connection."""
        if self._connection:
            self._connection.close()
        if self.engine:
            self.engine.dispose()

    async def fetch_batch(self, batch_size: Optional[int] = None) -> pd.DataFrame:
        """Fetch a batch of data from PostgreSQL."""
        size = batch_size or self.batch_size
        query = f"""
            SELECT *
            FROM {self.config.schema}.transactions
            ORDER BY transaction_timestamp DESC
            LIMIT {size}
        """
        try:
            return pd.read_sql(query, self._connection)
        except SQLAlchemyError as e:
            raise DataFetchError(f"Failed to fetch data from PostgreSQL: {str(e)}")

    async def stream_data(self) -> Generator[pd.DataFrame, None, None]:
        """Stream data from PostgreSQL in batches."""
        offset = 0
        while True:
            query = f"""
                SELECT *
                FROM {self.config.schema}.transactions
                ORDER BY transaction_timestamp DESC
                LIMIT {self.batch_size}
                OFFSET {offset}
            """
            try:
                df = pd.read_sql(query, self._connection)
                if df.empty:
                    break
                yield df
                offset += self.batch_size
            except SQLAlchemyError as e:
                raise DataFetchError(f"Failed to stream data from PostgreSQL: {str(e)}")


class DataFetchError(Exception):
    """Custom exception for data fetching errors."""
    pass 