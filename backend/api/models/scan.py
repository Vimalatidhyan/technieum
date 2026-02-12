"""Scan Pydantic schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ScanCreateRequest(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255)
    scan_type: str = Field(default="full")
    custom_phases: Optional[List[int]] = None
    model_config = {"json_schema_extra": {"example": {"domain": "example.com", "scan_type": "full"}}}

class ScanUpdateRequest(BaseModel):
    status: Optional[str] = None
    scan_type: Optional[str] = None

class ScanResponse(BaseModel):
    id: int
    domain: str
    scan_type: str
    status: str
    risk_score: Optional[int] = None
    phase: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class ScanListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[ScanResponse]
