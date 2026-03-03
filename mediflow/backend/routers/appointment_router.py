# ================================================================
#  routers/appointment_router.py — FIXED: UUID PKs, hashed_password chain
# ================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from mediflow_db.config import get_db
from mediflow_db.models import (
    Appointment, AppointmentData, TimeSlot, Patient,
    QueueEntry, PriorityScore, WaitTimeEstimate, AppointmentLog,
)
from auth import get_current_user, require_role
from algorithms.interval_tree import get_tree, Interval
from algorithms.priority_queue import get_queue, compute_score, QueueNode
from algorithms.wait_time import get_estimator
from algorithms.bipartite_matching import match_patients_to_slots

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


def _to_uuid(val):
    if val is None: return None
    if isinstance(val, uuid.UUID): return val
    try: return uuid.UUID(str(val))
    except ValueError: raise HTTPException(status_code=400, detail=f"Invalid UUID: {val}")


def _get_patient_age(db, patient_id_uuid):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id_uuid).first()
    if patient and patient.date_of_birth:
        return (datetime.utcnow().date() - patient.date_of_birth).days // 365
    return 30


@router.post("/", status_code=201)
def book_appointment(data: AppointmentData, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    p_id = _to_uuid(data.patient_id)
    d_id = _to_uuid(data.doctor_id)
    b_id = _to_uuid(data.branch_id)
    s_id = _to_uuid(data.slot_id) if data.slot_id else None

    if s_id:
        slot = db.query(TimeSlot).filter(TimeSlot.slot_id == s_id).first()
        if not slot: raise HTTPException(status_code=404, detail="Slot not found")
        if not slot.is_available: raise HTTPException(status_code=409, detail="Slot not available")

        tree = get_tree(str(d_id))
        start_dt = datetime.combine(slot.date, slot.start_time)
        end_dt   = datetime.combine(slot.date, slot.end_time)
        conflict = tree.has_conflict(str(d_id), start_dt, end_dt)
        if conflict:
            raise HTTPException(status_code=409, detail=f"Slot conflicts with existing appointment")

        slot.booked_count += 1
        if slot.booked_count >= slot.capacity:
            slot.is_available = False
        tree.insert(Interval(start=start_dt, end=end_dt, slot_id=str(s_id), doctor_id=str(d_id), branch_id=str(b_id)))

    appointment = Appointment(
        patient_id=p_id, doctor_id=d_id, branch_id=b_id, slot_id=s_id,
        urgency_level=data.urgency_level, appointment_type=data.appointment_type,
        scheduled_time=data.scheduled_time, notes=data.notes, booked_at=datetime.utcnow(),
    )
    db.add(appointment); db.flush()

    age    = _get_patient_age(db, p_id)
    scores = compute_score(urgency=data.urgency_level.value, appointment_type=data.appointment_type.value,
                           entered_at=datetime.utcnow(), age=age)

    pq          = get_queue(str(d_id), str(b_id))
    queue_depth = pq.size()
    position    = queue_depth + 1

    queue_entry = QueueEntry(
        appointment_id=appointment.appointment_id, branch_id=b_id, doctor_id=d_id,
        position=position, entered_queue_at=datetime.utcnow(), is_emergency=False,
    )
    db.add(queue_entry); db.flush()

    ps = PriorityScore(
        queue_id=queue_entry.queue_id, urgency_weight=0.50, wait_weight=0.30,
        age_weight=0.10, type_weight=0.10,
        raw_urgency_score=scores["raw_urgency_score"], raw_wait_score=scores["raw_wait_score"],
        raw_age_score=scores["raw_age_score"], raw_type_score=scores["raw_type_score"],
        final_score=scores["final_score"], computed_at=datetime.utcnow(),
    )
    db.add(ps)

    estimator = get_estimator(str(d_id), str(b_id))
    wait_data  = estimator.estimate(position, queue_depth + 1)
    wte = WaitTimeEstimate(
        queue_id=queue_entry.queue_id,
        estimated_wait_mins=wait_data["estimated_wait_mins"],
        queue_length=wait_data["queue_length"],
        service_rate=wait_data["service_rate"],
        calculated_at=datetime.utcnow(),
    )
    db.add(wte)
    queue_entry.estimated_wait_mins = int(wait_data["estimated_wait_mins"])

    node = QueueNode(
        neg_score=-scores["final_score"], appointment_id=str(appointment.appointment_id),
        patient_id=str(p_id), doctor_id=str(d_id), branch_id=str(b_id),
        urgency=data.urgency_level.value, appointment_type=data.appointment_type.value, age=age,
        entered_at=datetime.utcnow(),
    )
    pq.push(node)

    log = AppointmentLog(
        appointment_id=appointment.appointment_id, patient_id=p_id,
        doctor_id=d_id, branch_id=b_id, urgency_level=data.urgency_level,
        appointment_type=data.appointment_type, status=appointment.status,
        scheduled_time=data.scheduled_time, logged_at=datetime.utcnow(),
    )
    db.add(log); db.commit(); db.refresh(appointment)
    return _serialize(appointment)


@router.get("/")
def list_appointments(patient_id: str = None, doctor_id: str = None, branch_id: str = None,
                      skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                      _: dict = Depends(get_current_user)):
    q = db.query(Appointment)
    if patient_id:
        try: q = q.filter(Appointment.patient_id == uuid.UUID(patient_id))
        except ValueError: pass
    if doctor_id:
        try: q = q.filter(Appointment.doctor_id == uuid.UUID(doctor_id))
        except ValueError: pass
    if branch_id:
        try: q = q.filter(Appointment.branch_id == uuid.UUID(branch_id))
        except ValueError: pass
    return [_serialize(a) for a in q.offset(skip).limit(limit).all()]


@router.get("/{appointment_id}")
def get_appointment(appointment_id: str, db: Session = Depends(get_db),
                    _: dict = Depends(get_current_user)):
    try: aid = uuid.UUID(appointment_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid appointment ID")
    appt = db.query(Appointment).filter(Appointment.appointment_id == aid).first()
    if not appt: raise HTTPException(status_code=404, detail="Appointment not found")
    return _serialize(appt)


@router.patch("/{appointment_id}/complete")
def complete_appointment(appointment_id: str, duration_mins: float,
                         db: Session = Depends(get_db),
                         _: dict = Depends(require_role("doctor", "staff", "admin"))):
    try: aid = uuid.UUID(appointment_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid ID")
    appt = db.query(Appointment).filter(Appointment.appointment_id == aid).first()
    if not appt: raise HTTPException(status_code=404, detail="Not found")
    appt.status = "completed"; appt.actual_end_time = datetime.utcnow()
    estimator = get_estimator(str(appt.doctor_id), str(appt.branch_id))
    estimator.record_completion(duration_mins)
    pq = get_queue(str(appt.doctor_id), str(appt.branch_id))
    pq.remove(str(appointment_id))
    db.commit()
    return {"message": "Appointment completed", "duration_mins": duration_mins}


@router.patch("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db),
                       _: dict = Depends(get_current_user)):
    try: aid = uuid.UUID(appointment_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid ID")
    appt = db.query(Appointment).filter(Appointment.appointment_id == aid).first()
    if not appt: raise HTTPException(status_code=404, detail="Not found")
    appt.status = "cancelled"
    if appt.slot_id:
        slot = db.query(TimeSlot).filter(TimeSlot.slot_id == appt.slot_id).first()
        if slot:
            slot.booked_count = max(0, slot.booked_count - 1)
            slot.is_available = True
        tree = get_tree(str(appt.doctor_id))
        tree.remove(str(appt.slot_id))
    pq = get_queue(str(appt.doctor_id), str(appt.branch_id))
    pq.remove(str(appointment_id))
    db.commit()
    return {"message": "Appointment cancelled"}


def _serialize(a):
    return {
        "appointment_id": str(a.appointment_id), "patient_id": str(a.patient_id),
        "doctor_id": str(a.doctor_id), "branch_id": str(a.branch_id),
        "slot_id": str(a.slot_id) if a.slot_id else None,
        "urgency_level": a.urgency_level.value, "appointment_type": a.appointment_type.value,
        "status": a.status.value, "notes": a.notes,
        "scheduled_time": a.scheduled_time.isoformat() if a.scheduled_time else None,
        "booked_at": a.booked_at.isoformat() if a.booked_at else None,
    }
