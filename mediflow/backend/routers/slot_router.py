# ================================================================
#  routers/slot_router.py — FIXED: UUID slot/doctor/branch PKs
# ================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid

from mediflow_db.config import get_db
from mediflow_db.models import TimeSlot, TimeSlotData
from auth import get_current_user, require_role
from algorithms.interval_tree import get_tree, Interval

router = APIRouter(prefix="/api/slots", tags=["Time Slots"])

@router.post("/", status_code=201)
def create_slot(data: TimeSlotData, db: Session = Depends(get_db),
                _: dict = Depends(require_role("admin", "staff"))):
    try:
        d_id = uuid.UUID(data.doctor_id); b_id = uuid.UUID(data.branch_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid UUID")
    tree     = get_tree(str(d_id))
    start_dt = datetime.combine(data.date, data.start_time)
    end_dt   = datetime.combine(data.date, data.end_time)
    conflict = tree.has_conflict(str(d_id), start_dt, end_dt)
    if conflict: raise HTTPException(status_code=409, detail=f"Slot overlaps with existing slot")
    slot = TimeSlot(doctor_id=d_id, branch_id=b_id, date=data.date,
                    start_time=data.start_time, end_time=data.end_time, capacity=data.capacity)
    db.add(slot); db.flush()
    tree.insert(Interval(start=start_dt, end=end_dt, slot_id=str(slot.slot_id),
                         doctor_id=str(d_id), branch_id=str(b_id)))
    db.commit(); db.refresh(slot)
    return _serialize(slot)

@router.get("/available")
def get_available_slots(doctor_id: str, branch_id: str, date_str: str,
                        db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    try:
        d_id = uuid.UUID(doctor_id); b_id = uuid.UUID(branch_id)
        query_date = date.fromisoformat(date_str)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid input")
    slots = (db.query(TimeSlot)
             .filter(TimeSlot.doctor_id == d_id, TimeSlot.branch_id == b_id,
                     TimeSlot.date == query_date, TimeSlot.is_available == True)
             .order_by(TimeSlot.start_time).all())
    return [_serialize(s) for s in slots]

@router.delete("/{slot_id}")
def delete_slot(slot_id: str, db: Session = Depends(get_db),
                _: dict = Depends(require_role("admin", "staff"))):
    try: s_id = uuid.UUID(slot_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid UUID")
    slot = db.query(TimeSlot).filter(TimeSlot.slot_id == s_id).first()
    if not slot: raise HTTPException(status_code=404, detail="Slot not found")
    tree = get_tree(str(slot.doctor_id))
    tree.remove(slot_id)
    db.delete(slot); db.commit()
    return {"message": f"Slot {slot_id} deleted"}

def _serialize(s):
    return {"slot_id": str(s.slot_id), "doctor_id": str(s.doctor_id), "branch_id": str(s.branch_id),
            "date": str(s.date), "start_time": str(s.start_time), "end_time": str(s.end_time),
            "is_available": s.is_available, "is_peak_hour": s.is_peak_hour, "booked_count": s.booked_count}
