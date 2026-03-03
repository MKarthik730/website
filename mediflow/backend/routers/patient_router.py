# ================================================================
#  routers/patient_router.py — FIXED: UUID patient_id PK
# ================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from mediflow_db.config import get_db
from mediflow_db.models import Patient, PatientData, PatientResponse
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.post("/", status_code=201)
def create_patient(data: PatientData, db: Session = Depends(get_db),
                   _: dict = Depends(require_role("admin", "staff"))):
    patient = Patient(**data.model_dump())
    db.add(patient); db.commit(); db.refresh(patient)
    return _serialize(patient)

@router.get("/")
def list_patients(skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                  _: dict = Depends(require_role("admin", "staff", "doctor"))):
    patients = db.query(Patient).filter(Patient.is_active == True).offset(skip).limit(limit).all()
    return [_serialize(p) for p in patients]

@router.get("/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    try: pid = uuid.UUID(patient_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid patient ID")
    patient = db.query(Patient).filter(Patient.patient_id == pid).first()
    if not patient: raise HTTPException(status_code=404, detail="Patient not found")
    return _serialize(patient)

@router.put("/{patient_id}")
def update_patient(patient_id: str, data: PatientData, db: Session = Depends(get_db),
                   _: dict = Depends(require_role("admin", "staff"))):
    try: pid = uuid.UUID(patient_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid patient ID")
    patient = db.query(Patient).filter(Patient.patient_id == pid).first()
    if not patient: raise HTTPException(status_code=404, detail="Patient not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(patient, k, v)
    db.commit(); db.refresh(patient)
    return _serialize(patient)

@router.delete("/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db),
                   _: dict = Depends(require_role("admin"))):
    try: pid = uuid.UUID(patient_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid patient ID")
    patient = db.query(Patient).filter(Patient.patient_id == pid).first()
    if not patient: raise HTTPException(status_code=404, detail="Patient not found")
    patient.is_active = False; db.commit()
    return {"message": f"Patient {patient_id} deactivated"}

def _serialize(p):
    return {
        "patient_id": str(p.patient_id), "full_name": p.full_name,
        "date_of_birth": str(p.date_of_birth) if p.date_of_birth else None,
        "gender": p.gender, "blood_group": p.blood_group,
        "phone": p.phone, "email": p.email, "address": p.address, "is_active": p.is_active,
    }
