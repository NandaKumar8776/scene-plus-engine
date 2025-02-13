"""
Factory class for creating and managing data source connectors.
"""
from typing import Dict, Type

from .base import BaseConnector, DataSourceConfig
from .postgres import PostgresConnector, PostgresConfig
from .api import APIConnector, APIConfig


class ConnectorFactory:
    """Factory class for creating data source connectors."""

    _connector_registry: Dict[str, Type[BaseConnector]] = {
        "postgres": PostgresConnector,
        "api": APIConnector
    }

    _config_registry: Dict[str, Type[DataSourceConfig]] = {
        "postgres": PostgresConfig,
        "api": APIConfig
    }

    @classmethod
    def create_connector(cls, source_type: str, config_data: Dict) -> BaseConnector:
        """
        Create a connector instance based on source type and configuration.
        
        Args:
            source_type: Type of data source ("postgres", "api")
            config_data: Configuration dictionary for the connector
            
        Returns:
            BaseConnector: Instance of the appropriate connector
            
        Raises:
            ValueError: If source_type is not supported
        """
        if source_type not in cls._connector_registry:
            raise ValueError(f"Unsupported source type: {source_type}")

        connector_class = cls._connector_registry[source_type]
        config_class = cls._config_registry[source_type]
        
        # Create configuration instance
        config = config_class(**config_data)
        
        # Create and return connector instance
        return connector_class(config)

    @classmethod
    def register_connector(
        cls, 
        source_type: str, 
        connector_class: Type[BaseConnector],
        config_class: Type[DataSourceConfig]
    ) -> None:
        """
        Register a new connector type.
        
        Args:
            source_type: Type identifier for the connector
            connector_class: Connector class to register
            config_class: Configuration class for the connector
        """
        cls._connector_registry[source_type] = connector_class
        cls._config_registry[source_type] = config_class 