"""Finding Pydantic schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class FindingResponse(BaseModel):
    id: int
    scan_run_id: int
    vuln_type: str
    severity: Optional[int] = None
    title: str
    description: Optional[str] = None
    remediation: Optional[str] = None
    discovered_at: datetime
    model_config = {"from_attributes": True}

class FindingListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[FindingResponse]

class FindingUpdateRequest(BaseModel):
    severity: Optional[int] = None
    remediation: Optional[str] = None
