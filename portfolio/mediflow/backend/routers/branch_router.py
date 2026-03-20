# ================================================================
#  routers/branch_router.py — FIXED: UUID branch_id PKs
# ================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from mediflow_db.config import get_db
from mediflow_db.models import Branch, BranchData
from auth import get_current_user, require_role
from algorithms.kdtree import get_kdtree, rebuild_kdtree, BranchPoint
from algorithms.load_balancer import get_load_balancer, nearest_available_branch

router = APIRouter(prefix="/api/branches", tags=["Branches"])

@router.post("/", status_code=201)
def create_branch(data: BranchData, db: Session = Depends(get_db),
                  _: dict = Depends(require_role("admin"))):
    d = data.model_dump()
    try: d["hospital_id"] = uuid.UUID(d["hospital_id"])
    except (ValueError, TypeError): raise HTTPException(status_code=400, detail="Invalid hospital_id UUID")
    branch = Branch(**d)
    db.add(branch); db.commit(); db.refresh(branch)
    lb = get_load_balancer()
    lb.register(str(branch.branch_id), branch.total_capacity)
    all_branches = db.query(Branch).filter(Branch.is_active == True).all()
    rebuild_kdtree([{"branch_id": str(b.branch_id), "latitude": b.latitude or 0.0,
                     "longitude": b.longitude or 0.0, "is_active": b.is_active} for b in all_branches])
    return _serialize(branch)

@router.get("/")
def list_branches(db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    return [_serialize(b) for b in db.query(Branch).filter(Branch.is_active == True).all()]

@router.get("/nearest")
def find_nearest_branch(lat: float, lng: float, k: int = 3, _: dict = Depends(get_current_user)):
    kdtree  = get_kdtree()
    results = kdtree.k_nearest(lat, lng, k=k, only_available=True)
    if not results: return {"message": "No available branches found", "results": []}
    return {"results": [{"branch_id": r.branch_id, "lat": r.lat, "lng": r.lng} for r in results]}

@router.get("/load-summary")
def load_summary(_: dict = Depends(require_role("admin", "staff"))):
    lb = get_load_balancer()
    return lb.get_load_summary()

@router.get("/suggest-routing")
def suggest_routing(origin_branch_id: str, db: Session = Depends(get_db),
                    _: dict = Depends(get_current_user)):
    lb      = get_load_balancer()
    summary = lb.get_load_summary()
    overloaded = {s["branch_id"] for s in summary if s["is_overloaded"]}
    if origin_branch_id not in overloaded:
        return {"message": "Branch is not overloaded. No redirect needed."}
    all_branches = db.query(Branch).filter(Branch.is_active == True).all()
    coords  = {str(b.branch_id): (b.latitude or 0.0, b.longitude or 0.0) for b in all_branches}
    nearest = nearest_available_branch(origin_branch_id, coords, overloaded)
    if not nearest: return {"message": "No available branch found for redirect"}
    try: bid = uuid.UUID(nearest)
    except ValueError: bid = None
    branch = db.query(Branch).filter(Branch.branch_id == bid).first() if bid else None
    return {"redirect_to": nearest, "branch_name": branch.branch_name if branch else None,
            "reason": "Origin branch overloaded (>80% capacity)"}

@router.get("/next-assignment")
def next_assignment(_: dict = Depends(require_role("admin", "staff"))):
    lb = get_load_balancer()
    branch_id = lb.next_branch(exclude=[])
    return {"assigned_branch_id": branch_id}

@router.put("/{branch_id}/load")
def update_branch_load(branch_id: str, current_load: int,
                       _: dict = Depends(require_role("admin", "staff"))):
    lb = get_load_balancer()
    lb.update_load(branch_id, current_load)
    return {"message": "Load updated"}

def _serialize(b):
    return {
        "branch_id": str(b.branch_id), "hospital_id": str(b.hospital_id),
        "branch_name": b.branch_name, "city": b.city,
        "total_capacity": b.total_capacity, "current_load": b.current_load,
        "latitude": b.latitude, "longitude": b.longitude, "is_active": b.is_active,
    }
