"""
Data validation schemas for Scene+ data pipeline.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class RetailTransaction(BaseModel):
    """Schema for retail transaction data."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    store_id: str = Field(..., description="Store identifier")
    customer_id: str = Field(..., description="Customer identifier")
    transaction_timestamp: datetime = Field(..., description="Transaction timestamp")
    total_amount: float = Field(..., ge=0, description="Total transaction amount")
    banner: str = Field(..., description="Retail banner (Sobeys, Safeway, etc.)")
    items: List[dict] = Field(..., description="List of items purchased")
    payment_method: str = Field(..., description="Payment method used")
    points_earned: Optional[float] = Field(0.0, description="Scene+ points earned")
    
    @validator('items')
    def validate_items(cls, v):
        """Validate items structure."""
        if not v:
            raise ValueError("Transaction must have at least one item")
        for item in v:
            if not all(k in item for k in ['sku', 'quantity', 'price']):
                raise ValueError("Each item must have sku, quantity, and price")
        return v


class SceneTransaction(BaseModel):
    """Schema for Scene+ transaction data."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    member_id: str = Field(..., description="Scene+ member identifier")
    transaction_type: str = Field(..., description="Type of transaction (earn/redeem)")
    points: float = Field(..., description="Points earned or redeemed")
    transaction_timestamp: datetime = Field(..., description="Transaction timestamp")
    partner: str = Field(..., description="Partner where transaction occurred")
    source_transaction_id: Optional[str] = Field(None, description="Original transaction ID")
    
    @validator('transaction_type')
    def validate_transaction_type(cls, v):
        """Validate transaction type."""
        valid_types = ['earn', 'redeem']
        if v.lower() not in valid_types:
            raise ValueError(f"Transaction type must be one of {valid_types}")
        return v.lower()


class CustomerProfile(BaseModel):
    """Schema for customer profile data."""
    customer_id: str = Field(..., description="Customer identifier")
    scene_member_id: Optional[str] = Field(None, description="Scene+ member identifier")
    join_date: datetime = Field(..., description="Customer join date")
    total_points: float = Field(0.0, ge=0, description="Total Scene+ points balance")
    tier: str = Field("standard", description="Customer tier")
    preferred_banner: Optional[str] = Field(None, description="Most frequented banner")
    active_status: bool = Field(True, description="Whether customer is active")
    
    @validator('tier')
    def validate_tier(cls, v):
        """Validate customer tier."""
        valid_tiers = ['standard', 'silver', 'gold', 'platinum']
        if v.lower() not in valid_tiers:
            raise ValueError(f"Tier must be one of {valid_tiers}")
        return v.lower()


class PartnerTransaction(BaseModel):
    """Schema for partner (Cineplex, Scotiabank) transaction data."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    partner_id: str = Field(..., description="Partner identifier")
    member_id: str = Field(..., description="Scene+ member identifier")
    transaction_timestamp: datetime = Field(..., description="Transaction timestamp")
    transaction_type: str = Field(..., description="Type of transaction")
    amount: float = Field(..., ge=0, description="Transaction amount")
    points: float = Field(..., description="Points earned or redeemed")
    location: Optional[str] = Field(None, description="Transaction location")
    
    @validator('partner_id')
    def validate_partner(cls, v):
        """Validate partner identifier."""
        valid_partners = ['cineplex', 'scotiabank']
        if v.lower() not in valid_partners:
            raise ValueError(f"Partner must be one of {valid_partners}")
        return v.lower() 