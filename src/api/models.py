"""
API data models using Pydantic.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    """Customer profile data model."""
    customer_id: str = Field(..., description="Unique customer identifier")
    segment_id: Optional[int] = Field(None, description="Customer segment ID")
    segment_description: Optional[str] = Field(None, description="Segment description")
    total_points: float = Field(0.0, description="Total Scene+ points balance")
    preferred_banner: Optional[str] = Field(None, description="Most frequented banner")
    join_date: datetime = Field(..., description="Customer join date")
    last_activity: Optional[datetime] = Field(None, description="Last transaction date")


class OfferRequest(BaseModel):
    """Request model for offer generation."""
    customer_id: str = Field(..., description="Customer ID to generate offers for")
    count: int = Field(3, ge=1, le=10, description="Number of offers to generate")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class OfferResponse(BaseModel):
    """Response model for offers."""
    offer_id: str = Field(..., description="Unique offer identifier")
    offer_type: str = Field(..., description="Type of offer")
    value: float = Field(..., description="Offer value")
    conditions: Dict[str, Any] = Field(..., description="Offer conditions")
    start_date: datetime = Field(..., description="Offer start date")
    end_date: datetime = Field(..., description="Offer end date")
    target_banners: Optional[List[str]] = Field(None, description="Target banners")
    target_categories: Optional[List[str]] = Field(None, description="Target categories")


class OfferList(BaseModel):
    """List of offers with metadata."""
    customer_id: str = Field(..., description="Customer ID")
    generated_at: datetime = Field(default_factory=datetime.now)
    offers: List[OfferResponse] = Field(..., description="List of offers")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class OfferEvent(BaseModel):
    """Offer event tracking model."""
    event_id: str = Field(..., description="Unique event identifier")
    customer_id: str = Field(..., description="Customer ID")
    offer_id: str = Field(..., description="Offer ID")
    event_type: str = Field(..., description="Event type (view/click/redeem)")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Event metadata")


class ErrorResponse(BaseModel):
    """Error response model."""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details") 