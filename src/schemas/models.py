from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional


class URLCreate(BaseModel):
    original_url: str = Field(
        ..., 
        min_length=1, 
        max_length=2048, 
        description="The original long URL to shorten",
        examples=["https://www.example.com/very/long/url/path"]
    )
    custom_alias: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=20, 
        description="Optional custom short code (3-20 chars)",
        examples=["mylink", "blog-post"]
    )
    expires_at: Optional[datetime] = Field(
        None, 
        description="Optional expiration date for the short URL"
    )
    
    @field_validator('custom_alias')
    @classmethod
    def validate_custom_alias(cls, v):
        
        if v is not None:
            
            if not all(c.isalnum() or c in '-_' for c in v):
                raise ValueError(
                    'Custom alias can only contain alphanumeric characters, hyphens, and underscores'
                )
        return v
    
   
class URLResponse(BaseModel):
   
    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    click_count: int
    
    class Config:
        from_attributes = True


class ClickResponse(BaseModel):
    
    id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    referer: Optional[str]
    clicked_at: datetime
    
    class Config:
        from_attributes = True


class URLStats(BaseModel):
    
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    last_accessed: Optional[datetime]
    recent_clicks: list[ClickResponse] = []
    
    class Config:
        from_attributes = True