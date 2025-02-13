"""
Example usage of the Scene+ data transformation pipeline.
"""
import asyncio
import pandas as pd
from typing import Dict, Any

from connectors.factory import ConnectorFactory
from transformers.retail import RetailTransformer
from transformers.scene import SceneTransformer
from transformers.partner import PartnerTransformer


async def process_retail_data(connector: Any, transformer: RetailTransformer) -> Dict[str, Any]:
    """Process retail transaction data."""
    results = {
        'source': 'retail',
        'raw_record_count': 0,
        'valid_record_count': 0,
        'error_count': 0,
        'sample_data': None,
        'error_samples': None
    }
    
    async with connector as conn:
        # Fetch data
        raw_data = await conn.fetch_batch(batch_size=1000)
        results['raw_record_count'] = len(raw_data)
        
        # Transform data
        transformed_data = transformer.transform(raw_data)
        results['valid_record_count'] = len(transformed_data)
        results['error_count'] = len(transformer.error_records)
        
        # Store samples
        results['sample_data'] = transformed_data.head() if not transformed_data.empty else None
        results['error_samples'] = transformer.get_error_report().head() if transformer.error_records else None
    
    return results


async def process_scene_data(connector: Any, transformer: SceneTransformer) -> Dict[str, Any]:
    """Process Scene+ transaction data."""
    results = {
        'source': 'scene_plus',
        'raw_record_count': 0,
        'valid_record_count': 0,
        'error_count': 0,
        'sample_data': None,
        'error_samples': None,
        'member_metrics': None
    }
    
    async with connector as conn:
        # Fetch data
        raw_data = await conn.fetch_batch(batch_size=1000)
        results['raw_record_count'] = len(raw_data)
        
        # Transform data
        transformed_data = transformer.transform(raw_data)
        results['valid_record_count'] = len(transformed_data)
        results['error_count'] = len(transformer.error_records)
        
        # Calculate member metrics
        if not transformed_data.empty:
            results['member_metrics'] = transformer.aggregate_member_points(transformed_data)
        
        # Store samples
        results['sample_data'] = transformed_data.head() if not transformed_data.empty else None
        results['error_samples'] = transformer.get_error_report().head() if transformer.error_records else None
    
    return results


async def process_partner_data(connector: Any, transformer: PartnerTransformer) -> Dict[str, Any]:
    """Process partner transaction data."""
    results = {
        'source': 'partner',
        'raw_record_count': 0,
        'valid_record_count': 0,
        'error_count': 0,
        'sample_data': None,
        'error_samples': None,
        'partner_metrics': None,
        'partner_activity': None
    }
    
    async with connector as conn:
        # Fetch data
        raw_data = await conn.fetch_batch(batch_size=1000)
        results['raw_record_count'] = len(raw_data)
        
        # Transform data
        transformed_data = transformer.transform(raw_data)
        results['valid_record_count'] = len(transformed_data)
        results['error_count'] = len(transformer.error_records)
        
        # Calculate metrics
        if not transformed_data.empty:
            results['partner_metrics'] = transformer.get_partner_metrics(transformed_data)
            results['partner_activity'] = transformer.aggregate_partner_activity(transformed_data)
        
        # Store samples
        results['sample_data'] = transformed_data.head() if not transformed_data.empty else None
        results['error_samples'] = transformer.get_error_report().head() if transformer.error_records else None
    
    return results


async def main():
    """Run the data transformation pipeline example."""
    try:
        # Initialize transformers
        retail_transformer = RetailTransformer()
        scene_transformer = SceneTransformer()
        partner_transformer = PartnerTransformer()
        
        # Create connectors (using example configs from previous example.py)
        retail_connector = ConnectorFactory.create_connector("postgres", {
            "name": "retail",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "scene_plus_db",
            "user": "user",
            "password": "password",
            "schema": "retail"
        })
        
        scene_connector = ConnectorFactory.create_connector("api", {
            "name": "scene_plus",
            "type": "api",
            "base_url": "https://api.scene-plus.ca",
            "api_key": "example-key",
            "endpoints": {
                "transactions": "/v1/transactions"
            }
        })
        
        partner_connector = ConnectorFactory.create_connector("api", {
            "name": "partner",
            "type": "api",
            "base_url": "https://api.partner.com",
            "api_key": "example-key",
            "endpoints": {
                "transactions": "/v1/transactions"
            }
        })
        
        # Process data from all sources
        results = await asyncio.gather(
            process_retail_data(retail_connector, retail_transformer),
            process_scene_data(scene_connector, scene_transformer),
            process_partner_data(partner_connector, partner_transformer)
        )
        
        # Print results
        for source_results in results:
            print(f"\nResults for {source_results['source']}:")
            print(f"Raw records: {source_results['raw_record_count']}")
            print(f"Valid records: {source_results['valid_record_count']}")
            print(f"Errors: {source_results['error_count']}")
            
            if source_results['sample_data'] is not None:
                print("\nSample transformed data:")
                print(source_results['sample_data'])
            
            if source_results['error_samples'] is not None:
                print("\nSample errors:")
                print(source_results['error_samples'])
            
            # Print additional metrics if available
            if 'member_metrics' in source_results and source_results['member_metrics'] is not None:
                print("\nMember metrics:")
                print(source_results['member_metrics'].head())
            
            if 'partner_metrics' in source_results and source_results['partner_metrics'] is not None:
                print("\nPartner metrics:")
                print(source_results['partner_metrics'])
    
    except Exception as e:
        print(f"Error running pipeline: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 