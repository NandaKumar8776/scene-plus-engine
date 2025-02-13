"""
FastAPI endpoints for Scene+ recommendation service.
"""
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import (
    CustomerProfile, OfferRequest, OfferResponse, OfferList,
    OfferEvent, ErrorResponse
)
from models.customer_segmentation import CustomerSegmentation
from models.recommendation import RecommendationEngine, Offer
from data_pipeline.connectors.factory import ConnectorFactory


app = FastAPI(
    title="Scene+ Recommendation API",
    description="API for personalized Scene+ offers and recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
segmentation_model = CustomerSegmentation(n_clusters=5)
recommendation_engine = RecommendationEngine()

# Load pre-trained models
try:
    segmentation_model.load_model("models/customer_segmentation_model.joblib")
except Exception as e:
    print(f"Warning: Could not load segmentation model: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/customer/{customer_id}", response_model=CustomerProfile)
async def get_customer_profile(customer_id: str):
    """Get customer profile with segment information."""
    try:
        # Get customer data from database
        connector = ConnectorFactory.create_connector("postgres", {
            "name": "retail",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "scene_plus_db",
            "user": "user",
            "password": "password",
            "schema": "retail"
        })
        
        async with connector as conn:
            customer_data = await conn.fetch_customer(customer_id)
            
        if not customer_data:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} not found"
            )
        
        # Get customer segment
        segment = segmentation_model.predict(customer_data)
        
        return CustomerProfile(
            customer_id=customer_id,
            segment_id=segment['segment'].iloc[0],
            segment_description=segment['segment_description'].iloc[0],
            total_points=customer_data['total_points'].iloc[0],
            preferred_banner=customer_data['preferred_banner'].iloc[0],
            join_date=customer_data['join_date'].iloc[0],
            last_activity=customer_data['last_activity'].iloc[0]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/offers/generate", response_model=OfferList)
async def generate_offers(request: OfferRequest, background_tasks: BackgroundTasks):
    """Generate personalized offers for a customer."""
    try:
        # Get customer data
        connector = ConnectorFactory.create_connector("postgres", {
            "name": "retail",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "scene_plus_db",
            "user": "user",
            "password": "password",
            "schema": "retail"
        })
        
        async with connector as conn:
            customer_data = await conn.fetch_customer(request.customer_id)
            
        if not customer_data:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {request.customer_id} not found"
            )
        
        # Generate offers
        customer_offers = recommendation_engine.generate_offers(
            customer_data,
            segmentation_model.predict(customer_data),
            n_offers=request.count
        )
        
        # Convert offers to response format
        offers = []
        for offer in customer_offers[request.customer_id]:
            offer_dict = offer.to_dict()
            offer_dict['offer_id'] = str(uuid.uuid4())
            offers.append(OfferResponse(**offer_dict))
        
        # Track offer generation in background
        background_tasks.add_task(
            track_offer_event,
            customer_id=request.customer_id,
            offers=[o.offer_id for o in offers],
            event_type="generate"
        )
        
        return OfferList(
            customer_id=request.customer_id,
            offers=offers,
            metadata={"context": request.context}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/offers/track", response_model=OfferEvent)
async def track_offer_event(
    event: OfferEvent,
    background_tasks: BackgroundTasks
):
    """Track offer-related events."""
    try:
        # Validate event type
        valid_events = ["view", "click", "redeem"]
        if event.event_type not in valid_events:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event type. Must be one of: {valid_events}"
            )
        
        # Store event in database
        connector = ConnectorFactory.create_connector("postgres", {
            "name": "retail",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "scene_plus_db",
            "user": "user",
            "password": "password",
            "schema": "retail"
        })
        
        async with connector as conn:
            await conn.store_offer_event(event.dict())
        
        # Update offer metrics in background
        background_tasks.add_task(
            update_offer_metrics,
            offer_id=event.offer_id,
            event_type=event.event_type
        )
        
        return event
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/offers/{offer_id}", response_model=OfferResponse)
async def get_offer(offer_id: str):
    """Get details of a specific offer."""
    try:
        connector = ConnectorFactory.create_connector("postgres", {
            "name": "retail",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "scene_plus_db",
            "user": "user",
            "password": "password",
            "schema": "retail"
        })
        
        async with connector as conn:
            offer_data = await conn.fetch_offer(offer_id)
            
        if not offer_data:
            raise HTTPException(
                status_code=404,
                detail=f"Offer {offer_id} not found"
            )
        
        return OfferResponse(**offer_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


async def update_offer_metrics(offer_id: str, event_type: str):
    """Background task to update offer metrics."""
    try:
        connector = ConnectorFactory.create_connector("postgres", {
            "name": "retail",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "scene_plus_db",
            "user": "user",
            "password": "password",
            "schema": "retail"
        })
        
        async with connector as conn:
            await conn.update_offer_metrics(offer_id, event_type)
            
    except Exception as e:
        print(f"Error updating offer metrics: {e}")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=str(exc.status_code),
            message=exc.detail,
            details={"path": str(request.url)}
        ).dict()
    ) 