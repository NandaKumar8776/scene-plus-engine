"""
Example usage of the Scene+ data pipeline connectors.
"""
import asyncio
import os
from typing import Dict

import pandas as pd
from dotenv import load_dotenv

from connectors.factory import ConnectorFactory


async def main():
    """Example of using the data pipeline connectors."""
    # Load environment variables
    load_dotenv()

    # Configure PostgreSQL connector for retail data
    postgres_config = {
        "name": "retail",
        "type": "postgres",
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "schema": "retail"
    }

    # Configure API connector for Scene+ data
    scene_config = {
        "name": "scene_plus",
        "type": "api",
        "base_url": os.getenv("SCENE_API_URL"),
        "api_key": os.getenv("SCENE_API_KEY"),
        "api_secret": os.getenv("SCENE_API_SECRET"),
        "endpoints": {
            "transactions": "/v1/transactions",
            "members": "/v1/members",
            "points": "/v1/points"
        }
    }

    try:
        # Create connectors
        retail_connector = ConnectorFactory.create_connector("postgres", postgres_config)
        scene_connector = ConnectorFactory.create_connector("api", scene_config)

        # Example: Fetch retail transactions
        async with retail_connector as conn:
            retail_data = await conn.fetch_batch(batch_size=100)
            print("\nRetail Transactions Sample:")
            print(retail_data.head())

        # Example: Fetch Scene+ transactions
        async with scene_connector as conn:
            scene_data = await conn.fetch_batch(batch_size=100)
            print("\nScene+ Transactions Sample:")
            print(scene_data.head())

        # Example: Stream data
        print("\nStreaming retail data...")
        async with retail_connector as conn:
            async for batch in conn.stream_data():
                print(f"Received batch of {len(batch)} records")
                # Process batch here
                break  # Just showing first batch for example

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 