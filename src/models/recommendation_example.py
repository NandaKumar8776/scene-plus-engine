"""
Example usage of the Scene+ recommendation engine.
"""
import asyncio
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
import json

from data_pipeline.connectors.factory import ConnectorFactory
from data_pipeline.transformers.retail import RetailTransformer
from customer_segmentation import CustomerSegmentation
from recommendation import RecommendationEngine, Offer


def format_offer(offer: Offer) -> str:
    """Format offer details for display."""
    offer_dict = offer.to_dict()
    
    # Format basic offer details
    details = [
        f"Type: {offer_dict['offer_type']}",
        f"Value: {_format_value(offer_dict['offer_type'], offer_dict['value'])}"
    ]
    
    # Format conditions
    for condition, value in offer_dict['conditions'].items():
        details.append(f"{condition.replace('_', ' ').title()}: ${value:.2f}")
    
    # Format dates
    details.append(f"Valid: {offer_dict['start_date']} to {offer_dict['end_date']}")
    
    # Format targets if present
    if offer_dict['target_banners']:
        details.append(f"Valid at: {', '.join(offer_dict['target_banners'])}")
    if offer_dict['target_categories']:
        details.append(f"Valid for: {', '.join(offer_dict['target_categories'])}")
    
    return "\n".join(details)


def _format_value(offer_type: str, value: float) -> str:
    """Format offer value based on type."""
    if offer_type == "points_multiplier":
        return f"{value}x Points"
    elif offer_type in ["points_bonus", "threshold_bonus"]:
        return f"{value:,.0f} Bonus Points"
    elif offer_type == "category_discount":
        return f"{value*100:.0f}% Off"
    return str(value)


def save_recommendations(
    customer_offers: Dict[str, List[Offer]],
    filename: str = "recommendations.json"
) -> None:
    """Save recommendations to a JSON file."""
    formatted_offers = {
        customer_id: [offer.to_dict() for offer in offers]
        for customer_id, offers in customer_offers.items()
    }
    
    with open(filename, 'w') as f:
        json.dump(formatted_offers, f, indent=2)


async def main():
    """Run recommendation engine example."""
    try:
        # Initialize components
        retail_transformer = RetailTransformer()
        segmentation_model = CustomerSegmentation(n_clusters=5)
        recommendation_engine = RecommendationEngine()
        
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
        async with retail_connector as conn:
            raw_data = await conn.fetch_batch(batch_size=10000)
            retail_data = retail_transformer.transform(raw_data)
        
        # Generate customer segments
        print("\nGenerating customer segments...")
        segmentation_model.train(retail_data)
        customer_segments = segmentation_model.predict(retail_data)
        
        # Generate personalized offers
        print("\nGenerating personalized offers...")
        customer_offers = recommendation_engine.generate_offers(
            retail_data,
            customer_segments,
            n_offers=3
        )
        
        # Analyze recommendations
        total_customers = len(customer_offers)
        total_offers = sum(len(offers) for offers in customer_offers.values())
        avg_offers = total_offers / total_customers
        
        offer_types = {}
        for offers in customer_offers.values():
            for offer in offers:
                offer_types[offer.offer_type] = offer_types.get(offer.offer_type, 0) + 1
        
        # Print summary
        print("\nRecommendation Summary:")
        print(f"Total Customers: {total_customers}")
        print(f"Total Offers Generated: {total_offers}")
        print(f"Average Offers per Customer: {avg_offers:.1f}")
        print("\nOffer Type Distribution:")
        for offer_type, count in offer_types.items():
            percentage = (count / total_offers) * 100
            print(f"{offer_type}: {count} ({percentage:.1f}%)")
        
        # Print sample recommendations
        print("\nSample Recommendations:")
        sample_customer = list(customer_offers.keys())[0]
        print(f"\nCustomer ID: {sample_customer}")
        for i, offer in enumerate(customer_offers[sample_customer], 1):
            print(f"\nOffer {i}:")
            print(format_offer(offer))
        
        # Save recommendations
        print("\nSaving recommendations...")
        save_recommendations(customer_offers)
        
        print("\nRecommendations complete! Check recommendations.json for full details.")
        
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 