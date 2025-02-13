"""
Example usage of the Scene+ customer segmentation model.
"""
import asyncio
import pandas as pd
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns

from data_pipeline.connectors.factory import ConnectorFactory
from data_pipeline.transformers.retail import RetailTransformer
from customer_segmentation import CustomerSegmentation


async def get_retail_data(connector: Any, transformer: RetailTransformer) -> pd.DataFrame:
    """Fetch and transform retail transaction data."""
    async with connector as conn:
        raw_data = await conn.fetch_batch(batch_size=10000)
        return transformer.transform(raw_data)


def visualize_segments(segment_profiles: pd.DataFrame, save_path: str = None):
    """Create visualization of segment profiles."""
    # Prepare data for visualization
    features = segment_profiles.drop(['segment', 'description'], axis=1)
    
    # Create heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        features,
        cmap='RdYlBu_r',
        center=0,
        annot=True,
        fmt='.2f',
        yticklabels=segment_profiles['description']
    )
    plt.title('Customer Segment Profiles')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def analyze_segments(segments: pd.DataFrame, profiles: pd.DataFrame) -> Dict[str, Any]:
    """Analyze segment distribution and characteristics."""
    analysis = {
        'segment_distribution': segments['segment'].value_counts().to_dict(),
        'segment_percentages': (segments['segment'].value_counts(normalize=True) * 100).to_dict(),
        'segment_profiles': profiles.to_dict('records'),
        'total_customers': len(segments)
    }
    return analysis


async def main():
    """Run customer segmentation example."""
    try:
        # Initialize components
        retail_transformer = RetailTransformer()
        segmentation_model = CustomerSegmentation(n_clusters=5)
        
        # Create connector
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
        
        # Get and transform data
        print("Fetching and transforming retail data...")
        retail_data = await get_retail_data(retail_connector, retail_transformer)
        
        # Train segmentation model
        print("\nTraining customer segmentation model...")
        segmentation_model.train(retail_data)
        
        # Get customer segments
        print("\nGenerating customer segments...")
        customer_segments = segmentation_model.predict(retail_data)
        
        # Get segment profiles
        segment_profiles = segmentation_model.get_segment_profiles()
        
        # Analyze results
        analysis = analyze_segments(customer_segments, segment_profiles)
        
        # Print results
        print("\nCustomer Segmentation Results:")
        print(f"Total Customers: {analysis['total_customers']}")
        print("\nSegment Distribution:")
        for segment, count in analysis['segment_distribution'].items():
            description = segment_profiles.loc[segment_profiles['segment'] == segment, 'description'].iloc[0]
            percentage = analysis['segment_percentages'][segment]
            print(f"Segment {segment} ({description}): {count} customers ({percentage:.1f}%)")
        
        # Visualize results
        print("\nGenerating segment profile visualization...")
        visualize_segments(segment_profiles, 'segment_profiles.png')
        
        # Save model
        print("\nSaving model...")
        segmentation_model.save_model('customer_segmentation_model.joblib')
        
        print("\nSegmentation complete! Check segment_profiles.png for visualization.")
        
    except Exception as e:
        print(f"Error running segmentation: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 