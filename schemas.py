from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import TokenType, ConversionStatus

# Token Conversion Schemas
class TokenConversionRequest(BaseModel):
    raw_token: str = Field(..., min_length=10, description="Input EAT or Access Token")
    conversion_type: TokenType
    telegram_username: Optional[str] = None
    captcha_solution: str = Field(..., min_length=4)

class TokenConversionResponse(BaseModel):
    success: bool
    status: ConversionStatus
    converted_token: Optional[str] = None
    conversion_id: int
    message: str

# Conversion History
class ConversionItem(BaseModel):
    id: int
    conversion_type: TokenType
    result_token_hint: str
    status: ConversionStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Admin Schemas
class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_conversions: int
    failed_conversions: int
    today_conversions: int
    active_api_keys: int

class SystemConfigUpdate(BaseModel):
    maintenance_mode: bool
    telegram_alerts_active: bool