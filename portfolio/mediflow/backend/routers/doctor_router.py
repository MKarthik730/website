# ================================================================
#  routers/doctor_router.py — FIXED: UUID doctor_id PK
# ================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from mediflow_db.config import get_db
from mediflow_db.models import Doctor, DoctorData
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])

@router.post("/", status_code=201)
def create_doctor(data: DoctorData, db: Session = Depends(get_db),
                  _: dict = Depends(require_role("admin"))):
    d = data.model_dump()
    if d.get("department_id"):
        try: d["department_id"] = uuid.UUID(d["department_id"])
        except ValueError: d["department_id"] = None
    doctor = Doctor(**d)
    db.add(doctor); db.commit(); db.refresh(doctor)
    return _serialize(doctor)

@router.get("/")
def list_doctors(skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                 _: dict = Depends(get_current_user)):
    doctors = db.query(Doctor).filter(Doctor.is_active == True).offset(skip).limit(limit).all()
    return [_serialize(d) for d in doctors]

@router.get("/{doctor_id}")
def get_doctor(doctor_id: str, db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    try: did = uuid.UUID(doctor_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid doctor ID")
    doctor = db.query(Doctor).filter(Doctor.doctor_id == did).first()
    if not doctor: raise HTTPException(status_code=404, detail="Doctor not found")
    return _serialize(doctor)

@router.put("/{doctor_id}")
def update_doctor(doctor_id: str, data: DoctorData, db: Session = Depends(get_db),
                  _: dict = Depends(require_role("admin"))):
    try: did = uuid.UUID(doctor_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid doctor ID")
    doctor = db.query(Doctor).filter(Doctor.doctor_id == did).first()
    if not doctor: raise HTTPException(status_code=404, detail="Doctor not found")
    d = data.model_dump(exclude_unset=True)
    if "department_id" in d and d["department_id"]:
        try: d["department_id"] = uuid.UUID(d["department_id"])
        except ValueError: d["department_id"] = None
    for k, v in d.items(): setattr(doctor, k, v)
    db.commit(); db.refresh(doctor)
    return _serialize(doctor)

@router.delete("/{doctor_id}")
def deactivate_doctor(doctor_id: str, db: Session = Depends(get_db),
                      _: dict = Depends(require_role("admin"))):
    try: did = uuid.UUID(doctor_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid doctor ID")
    doctor = db.query(Doctor).filter(Doctor.doctor_id == did).first()
    if not doctor: raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_active = False; db.commit()
    return {"message": f"Doctor {doctor_id} deactivated"}

def _serialize(d):
    return {
        "doctor_id": str(d.doctor_id), "full_name": d.full_name,
        "specialization": d.specialization, "qualification": d.qualification,
        "experience_yrs": d.experience_yrs, "avg_consult_mins": d.avg_consult_mins,
        "phone": d.phone, "email": d.email,
        "department_id": str(d.department_id) if d.department_id else None,
        "is_active": d.is_active,
    }
