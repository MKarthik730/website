# ================================================================
#  routers/queue_router.py — FIXED: UUID queue_id PKs
# ================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from mediflow_db.config import get_db
from mediflow_db.models import (
    QueueEntry, PriorityScore, EmergencyOverride, EmergencyOverrideData, Appointment,
)
from auth import get_current_user, require_role
from algorithms.priority_queue import get_queue, QueueNode
from algorithms.wait_time import get_estimator

router = APIRouter(prefix="/api/queue", tags=["Queue"])


@router.get("/live/{doctor_id}/{branch_id}")
def get_live_queue(doctor_id: str, branch_id: str, db: Session = Depends(get_db),
                   _: dict = Depends(get_current_user)):
    try: d_id = uuid.UUID(doctor_id); b_id = uuid.UUID(branch_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid UUID")

    entries = (
        db.query(QueueEntry)
        .filter(QueueEntry.doctor_id == d_id, QueueEntry.branch_id == b_id,
                QueueEntry.status.in_(["waiting", "called"]))
        .join(PriorityScore, PriorityScore.queue_id == QueueEntry.queue_id)
        .order_by(PriorityScore.final_score.desc())
        .all()
    )
    return [{
        "position": idx + 1, "queue_id": str(e.queue_id),
        "appointment_id": str(e.appointment_id),
        "estimated_wait_mins": e.estimated_wait_mins, "is_emergency": e.is_emergency,
        "status": e.status.value,
        "priority_score": e.priority_score.final_score if e.priority_score else None,
    } for idx, e in enumerate(entries)]


@router.get("/next/{doctor_id}/{branch_id}")
def get_next_patient(doctor_id: str, branch_id: str,
                     _: dict = Depends(require_role("doctor", "staff", "admin"))):
    pq   = get_queue(doctor_id, branch_id)
    node = pq.pop()
    if not node: return {"message": "Queue is empty"}
    return {"appointment_id": node.appointment_id, "patient_id": node.patient_id,
            "urgency": node.urgency, "priority_score": -node.neg_score, "is_emergency": node.is_emergency}


@router.post("/emergency-override", status_code=201)
def emergency_override(data: EmergencyOverrideData, db: Session = Depends(get_db),
                       current_user: dict = Depends(require_role("doctor", "staff", "admin"))):
    try: q_id = uuid.UUID(data.queue_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid queue_id UUID")

    queue_entry = db.query(QueueEntry).filter(QueueEntry.queue_id == q_id).first()
    if not queue_entry: raise HTTPException(status_code=404, detail="Queue entry not found")

    appt = db.query(Appointment).filter(Appointment.appointment_id == queue_entry.appointment_id).first()
    if not appt: raise HTTPException(status_code=404, detail="Appointment not found")

    prev_position = queue_entry.position
    queue_entry.is_emergency    = True
    queue_entry.override_reason = data.reason
    queue_entry.position        = 1
    if queue_entry.priority_score:
        queue_entry.priority_score.final_score = 999.0
        queue_entry.priority_score.computed_at = datetime.utcnow()

    override = EmergencyOverride(
        queue_id=q_id, triggered_by=data.triggered_by or current_user.get("sub"),
        reason=data.reason, previous_position=prev_position, new_position=1,
        triggered_at=datetime.utcnow(),
    )
    db.add(override)

    pq = get_queue(str(queue_entry.doctor_id), str(queue_entry.branch_id))
    pq.remove(str(appt.appointment_id))
    node = QueueNode(
        neg_score=-999.0, appointment_id=str(appt.appointment_id),
        patient_id=str(appt.patient_id), doctor_id=str(appt.doctor_id),
        branch_id=str(appt.branch_id), urgency=appt.urgency_level.value,
        appointment_type=appt.appointment_type.value, is_emergency=True,
    )
    pq.push(node)
    db.commit(); db.refresh(override)
    return {"override_id": str(override.override_id), "queue_id": str(override.queue_id),
            "reason": override.reason, "previous_position": override.previous_position,
            "new_position": override.new_position,
            "triggered_at": override.triggered_at.isoformat() if override.triggered_at else None}


@router.get("/score/{queue_id}")
def get_priority_score(queue_id: str, db: Session = Depends(get_db),
                       _: dict = Depends(get_current_user)):
    try: q_id = uuid.UUID(queue_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid UUID")
    score = db.query(PriorityScore).filter(PriorityScore.queue_id == q_id).first()
    if not score: raise HTTPException(status_code=404, detail="Score not found")
    return {"score_id": str(score.score_id), "queue_id": str(score.queue_id),
            "final_score": score.final_score, "computed_at": score.computed_at.isoformat() if score.computed_at else None}


@router.post("/recalculate/{doctor_id}/{branch_id}")
def recalculate_queue(doctor_id: str, branch_id: str,
                      _: dict = Depends(require_role("admin", "staff"))):
    pq = get_queue(doctor_id, branch_id)
    pq.recalculate_all()
    return {"message": "Queue recalculated", "queue_size": pq.size()}


@router.patch("/status/{queue_id}")
def update_queue_status(queue_id: str, new_status: str, db: Session = Depends(get_db),
                        _: dict = Depends(require_role("doctor", "staff", "admin"))):
    try: q_id = uuid.UUID(queue_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid UUID")
    entry = db.query(QueueEntry).filter(QueueEntry.queue_id == q_id).first()
    if not entry: raise HTTPException(status_code=404, detail="Queue entry not found")
    valid = ["waiting", "called", "in_room", "done", "skipped"]
    if new_status not in valid: raise HTTPException(status_code=400, detail=f"Must be one of {valid}")
    entry.status = new_status; db.commit()
    return {"message": f"Status updated to {new_status}"}
