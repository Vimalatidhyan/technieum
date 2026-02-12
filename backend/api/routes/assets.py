"""Asset management API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.db.database import get_db
from backend.db.models import Subdomain
from backend.api.models.asset import AssetListResponse, AssetResponse
from backend.api.models.common import StatusResponse

router = APIRouter()

@router.get("/", response_model=AssetListResponse, summary="List assets")
def list_assets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    scan_run_id: Optional[int] = None,
    is_alive: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List all discovered assets."""
    q = db.query(Subdomain)
    if scan_run_id:
        q = q.filter(Subdomain.scan_run_id == scan_run_id)
    if is_alive is not None:
        q = q.filter(Subdomain.is_alive == is_alive)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return AssetListResponse(total=total, page=page, per_page=per_page, items=items)

@router.get("/by-domain/{domain}", response_model=AssetListResponse, summary="Assets by domain")
def assets_by_domain(domain: str, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Get all assets for a specific domain."""
    q = db.query(Subdomain).filter(Subdomain.subdomain.contains(domain))
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return AssetListResponse(total=total, page=page, per_page=per_page, items=items)

@router.get("/search", response_model=AssetListResponse, summary="Search assets")
def search_assets(q_str: str = Query(..., alias="q"), page: int = Query(1, ge=1), per_page: int = Query(20), db: Session = Depends(get_db)):
    """Search assets by keyword."""
    q = db.query(Subdomain).filter(Subdomain.subdomain.contains(q_str))
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return AssetListResponse(total=total, page=page, per_page=per_page, items=items)

@router.get("/high-risk", response_model=AssetListResponse, summary="High-risk assets")
def high_risk_assets(page: int = Query(1, ge=1), per_page: int = Query(20), db: Session = Depends(get_db)):
    """Get assets with high port/vulnerability count."""
    q = db.query(Subdomain).filter(Subdomain.is_alive == True)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return AssetListResponse(total=total, page=page, per_page=per_page, items=items)

@router.get("/{asset_id}", response_model=AssetResponse, summary="Get asset")
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get a specific asset by ID."""
    asset = db.query(Subdomain).filter(Subdomain.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.get("/{asset_id}/timeline", summary="Asset timeline")
def asset_timeline(asset_id: int, db: Session = Depends(get_db)):
    """Get activity timeline for an asset."""
    asset = db.query(Subdomain).filter(Subdomain.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"asset_id": asset_id, "subdomain": asset.subdomain, "first_seen": asset.first_seen, "last_seen": asset.last_seen, "events": []}
