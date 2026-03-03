# ================================================================
#  mediflow_db/models.py  — SINGLE SOURCE OF TRUTH
#  Aligned with real PostgreSQL schemas using UUID PKs
#  and hashed_password column name.
# ================================================================

import uuid
import enum
from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Date, Time, Text, ForeignKey, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from mediflow_db.config import Base


# ================================================================
#  ENUMS
# ================================================================

class RoleEnum(str, enum.Enum):
    patient = "patient"
    doctor  = "doctor"
    staff   = "staff"
    admin   = "admin"

class UrgencyEnum(str, enum.Enum):
    critical = "critical"
    high     = "high"
    medium   = "medium"
    low      = "low"

class AppointmentTypeEnum(str, enum.Enum):
    consultation = "consultation"
    surgery      = "surgery"
    follow_up    = "follow_up"
    emergency    = "emergency"

class AppointmentStatusEnum(str, enum.Enum):
    scheduled   = "scheduled"
    in_progress = "in_progress"
    completed   = "completed"
    cancelled   = "cancelled"
    no_show     = "no_show"

class QueueStatusEnum(str, enum.Enum):
    waiting = "waiting"
    called  = "called"
    in_room = "in_room"
    done    = "done"
    skipped = "skipped"


# ================================================================
#  SCHEMA: ORGANIZATION
# ================================================================

class Hospital(Base):
    __tablename__  = "hospitals"
    __table_args__ = {"schema": "organization"}

    hospital_id  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name         = Column(String(200), nullable=False, unique=True)
    chain_name   = Column(String(200), nullable=True)
    country      = Column(String(100), nullable=True)
    contact_info = Column(JSON, nullable=True)
    is_active    = Column(Boolean, default=True)

    branches = relationship("Branch", back_populates="hospital", cascade="all, delete-orphan")


class Branch(Base):
    __tablename__  = "branches"
    __table_args__ = {"schema": "organization"}

    branch_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id    = Column(UUID(as_uuid=True), ForeignKey("organization.hospitals.hospital_id"), nullable=False)
    branch_name    = Column(String(200), nullable=False)
    city           = Column(String(100), nullable=True)
    address        = Column(Text, nullable=True)
    latitude       = Column(Float, nullable=True)
    longitude      = Column(Float, nullable=True)
    total_capacity = Column(Integer, default=100)
    current_load   = Column(Float, default=0.0)
    is_active      = Column(Boolean, default=True)
    contact_info   = Column(JSON, nullable=True)

    hospital    = relationship("Hospital", back_populates="branches")
    departments = relationship("Department", back_populates="branch", cascade="all, delete-orphan")


class Department(Base):
    __tablename__  = "departments"
    __table_args__ = {"schema": "organization"}

    department_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id     = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=False)
    name          = Column(String(200), nullable=False)
    specialty     = Column(String(200), nullable=True)
    floor_number  = Column(Integer, nullable=True)
    is_active     = Column(Boolean, default=True)

    branch  = relationship("Branch", back_populates="departments")
    rooms   = relationship("Room", back_populates="department", cascade="all, delete-orphan")
    doctors = relationship("Doctor", back_populates="department")


class Room(Base):
    __tablename__  = "rooms"
    __table_args__ = {"schema": "organization"}

    room_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("organization.departments.department_id"), nullable=False)
    room_number   = Column(String(20), nullable=False)
    room_type     = Column(String(100), nullable=True)
    is_available  = Column(Boolean, default=True)

    department = relationship("Department", back_populates="rooms")


# ================================================================
#  SCHEMA: USERS
# ================================================================

class Patient(Base):
    __tablename__  = "patients"
    __table_args__ = {"schema": "users"}

    patient_id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name         = Column(String(200), nullable=False)
    date_of_birth     = Column(Date, nullable=True)
    gender            = Column(String(20), nullable=True)
    blood_group       = Column(String(5), nullable=True)
    phone             = Column(String(20), nullable=True)
    email             = Column(String(200), unique=True, nullable=True)
    address           = Column(String(500), nullable=True)
    emergency_contact = Column(JSON, nullable=True)
    medical_flags     = Column(JSON, nullable=True)
    is_active         = Column(Boolean, default=True)

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")


class Doctor(Base):
    __tablename__  = "doctors"
    __table_args__ = {"schema": "users"}

    doctor_id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id    = Column(UUID(as_uuid=True), ForeignKey("organization.departments.department_id"), nullable=True)
    full_name        = Column(String(200), nullable=False)
    specialization   = Column(String(200), nullable=True)
    qualification    = Column(String(500), nullable=True)
    experience_yrs   = Column(Integer, nullable=True)
    avg_consult_mins = Column(Float, default=15.0)
    phone            = Column(String(20), nullable=True)
    email            = Column(String(200), unique=True, nullable=True)
    is_active        = Column(Boolean, default=True)

    department   = relationship("Department", back_populates="doctors")
    time_slots   = relationship("TimeSlot", back_populates="doctor", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="doctor")


class Staff(Base):
    __tablename__  = "staff"
    __table_args__ = {"schema": "users"}

    staff_id  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=True)
    full_name = Column(String(200), nullable=False)
    role      = Column(String(100), nullable=True)
    phone     = Column(String(20), nullable=True)
    email     = Column(String(200), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)


class UserAuth(Base):
    __tablename__  = "user_auth"
    __table_args__ = {"schema": "users"}

    auth_id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_ref_id     = Column(UUID(as_uuid=True), nullable=False)
    role            = Column(Enum(RoleEnum), nullable=False)
    username        = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(500), nullable=False)   # FIX: was "password" in old models.py
    is_active       = Column(Boolean, default=True)
    refresh_token   = Column(String(500), nullable=True)


# ================================================================
#  SCHEMA: SCHEDULING
# ================================================================

class TimeSlot(Base):
    __tablename__  = "time_slots"
    __table_args__ = {"schema": "scheduling"}

    slot_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id    = Column(UUID(as_uuid=True), ForeignKey("users.doctors.doctor_id"), nullable=False)
    branch_id    = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=False)
    date         = Column(Date, nullable=False)
    start_time   = Column(Time, nullable=False)
    end_time     = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    is_peak_hour = Column(Boolean, default=False)
    load_factor  = Column(Float, default=0.0)
    capacity     = Column(Integer, default=1)
    booked_count = Column(Integer, default=0)

    doctor       = relationship("Doctor", back_populates="time_slots")
    appointments = relationship("Appointment", back_populates="slot")


class Appointment(Base):
    __tablename__  = "appointments"
    __table_args__ = {"schema": "scheduling"}

    appointment_id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id        = Column(UUID(as_uuid=True), ForeignKey("users.patients.patient_id"), nullable=False)
    doctor_id         = Column(UUID(as_uuid=True), ForeignKey("users.doctors.doctor_id"), nullable=False)
    branch_id         = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=False)
    slot_id           = Column(UUID(as_uuid=True), ForeignKey("scheduling.time_slots.slot_id"), nullable=True)
    urgency_level     = Column(Enum(UrgencyEnum), nullable=False)
    appointment_type  = Column(Enum(AppointmentTypeEnum), nullable=False)
    status            = Column(Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.scheduled)
    booked_at         = Column(DateTime, default=datetime.utcnow)
    scheduled_time    = Column(DateTime, nullable=False)
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time   = Column(DateTime, nullable=True)
    notes             = Column(Text, nullable=True)

    patient     = relationship("Patient", back_populates="appointments")
    doctor      = relationship("Doctor", back_populates="appointments")
    slot        = relationship("TimeSlot", back_populates="appointments")
    queue_entry = relationship("QueueEntry", back_populates="appointment", uselist=False, cascade="all, delete-orphan")


class SlotBlock(Base):
    __tablename__  = "slot_blocks"
    __table_args__ = {"schema": "scheduling"}

    block_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id      = Column(UUID(as_uuid=True), ForeignKey("users.doctors.doctor_id"), nullable=True)
    branch_id      = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime   = Column(DateTime, nullable=False)
    reason         = Column(String(300), nullable=True)


class Recurrence(Base):
    __tablename__  = "recurrences"
    __table_args__ = {"schema": "scheduling"}

    recurrence_id  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id     = Column(UUID(as_uuid=True), ForeignKey("users.patients.patient_id"), nullable=True)
    doctor_id      = Column(UUID(as_uuid=True), ForeignKey("users.doctors.doctor_id"), nullable=True)
    frequency      = Column(String(50), nullable=True)
    day_of_week    = Column(Integer, nullable=True)
    preferred_time = Column(Time, nullable=True)
    is_active      = Column(Boolean, default=True)


# ================================================================
#  SCHEMA: QUEUE
# ================================================================

class QueueEntry(Base):
    __tablename__  = "queue_entries"
    __table_args__ = {"schema": "queue"}

    queue_id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id      = Column(UUID(as_uuid=True), ForeignKey("scheduling.appointments.appointment_id"), nullable=False)
    branch_id           = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=False)
    doctor_id           = Column(UUID(as_uuid=True), ForeignKey("users.doctors.doctor_id"), nullable=False)
    position            = Column(Integer, nullable=False)
    entered_queue_at    = Column(DateTime, default=datetime.utcnow)
    estimated_wait_mins = Column(Integer, nullable=True)
    is_emergency        = Column(Boolean, default=False)
    override_reason     = Column(Text, nullable=True)
    status              = Column(Enum(QueueStatusEnum), default=QueueStatusEnum.waiting)

    appointment    = relationship("Appointment", back_populates="queue_entry")
    priority_score = relationship("PriorityScore", back_populates="queue_entry", uselist=False, cascade="all, delete-orphan")
    wait_estimate  = relationship("WaitTimeEstimate", back_populates="queue_entry", uselist=False, cascade="all, delete-orphan")


class PriorityScore(Base):
    __tablename__  = "priority_scores"
    __table_args__ = {"schema": "queue"}

    score_id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_id          = Column(UUID(as_uuid=True), ForeignKey("queue.queue_entries.queue_id"), nullable=False)
    urgency_weight    = Column(Float, default=0.50)
    wait_weight       = Column(Float, default=0.30)
    age_weight        = Column(Float, default=0.10)
    type_weight       = Column(Float, default=0.10)
    raw_urgency_score = Column(Integer, nullable=True)
    raw_wait_score    = Column(Float, nullable=True)
    raw_age_score     = Column(Integer, nullable=True)
    raw_type_score    = Column(Integer, nullable=True)
    final_score       = Column(Float, nullable=False)
    computed_at       = Column(DateTime, default=datetime.utcnow)

    queue_entry = relationship("QueueEntry", back_populates="priority_score")


class EmergencyOverride(Base):
    __tablename__  = "emergency_overrides"
    __table_args__ = {"schema": "queue"}

    override_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_id          = Column(UUID(as_uuid=True), ForeignKey("queue.queue_entries.queue_id"), nullable=False)
    triggered_by      = Column(String(200), nullable=True)  # FIX: was UUID FK to staff — now plain string (username)
    reason            = Column(Text, nullable=False)
    previous_position = Column(Integer, nullable=True)
    new_position      = Column(Integer, default=1)
    triggered_at      = Column(DateTime, default=datetime.utcnow)


class WaitTimeEstimate(Base):
    __tablename__  = "wait_time_estimates"
    __table_args__ = {"schema": "queue"}

    estimate_id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_id            = Column(UUID(as_uuid=True), ForeignKey("queue.queue_entries.queue_id"), nullable=False)
    estimated_wait_mins = Column(Float, nullable=True)
    queue_length        = Column(Integer, nullable=True)
    service_rate        = Column(Float, nullable=True)
    calculated_at       = Column(DateTime, default=datetime.utcnow)

    queue_entry = relationship("QueueEntry", back_populates="wait_estimate")


# ================================================================
#  SCHEMA: ANALYTICS
# ================================================================

class AppointmentLog(Base):
    __tablename__  = "appointment_logs"
    __table_args__ = {"schema": "analytics"}

    log_id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id        = Column(UUID(as_uuid=True), nullable=False)
    patient_id            = Column(UUID(as_uuid=True), nullable=False)
    doctor_id             = Column(UUID(as_uuid=True), nullable=False)
    branch_id             = Column(UUID(as_uuid=True), nullable=False)
    urgency_level         = Column(Enum(UrgencyEnum), nullable=True)
    appointment_type      = Column(Enum(AppointmentTypeEnum), nullable=True)
    status                = Column(Enum(AppointmentStatusEnum), nullable=True)
    scheduled_time        = Column(DateTime, nullable=True)
    actual_start_time     = Column(DateTime, nullable=True)
    actual_end_time       = Column(DateTime, nullable=True)
    wait_time_mins        = Column(Float, nullable=True)
    consult_duration_mins = Column(Float, nullable=True)
    logged_at             = Column(DateTime, default=datetime.utcnow)


class PeakHourStat(Base):
    __tablename__  = "peak_hour_stats"
    __table_args__ = {"schema": "analytics"}

    stat_id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id        = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=True)
    day_of_week      = Column(Integer, nullable=True)
    hour_of_day      = Column(Integer, nullable=True)
    avg_appointments = Column(Float, nullable=True)
    max_appointments = Column(Integer, nullable=True)
    avg_wait_mins    = Column(Float, nullable=True)
    recorded_on      = Column(Date, default=date.today)


class DoctorPerformance(Base):
    __tablename__  = "doctor_performance"
    __table_args__ = {"schema": "analytics"}

    perf_id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id          = Column(UUID(as_uuid=True), ForeignKey("users.doctors.doctor_id"), nullable=True)
    date               = Column(Date, default=date.today)
    total_appointments = Column(Integer, default=0)
    completed_count    = Column(Integer, default=0)
    no_show_count      = Column(Integer, default=0)
    avg_consult_mins   = Column(Float, nullable=True)
    avg_wait_mins      = Column(Float, nullable=True)
    utilization_pct    = Column(Float, nullable=True)


class BranchLoadStat(Base):
    __tablename__  = "branch_load_stats"
    __table_args__ = {"schema": "analytics"}

    load_id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id           = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=True)
    recorded_at         = Column(DateTime, default=datetime.utcnow)
    active_appointments = Column(Integer, nullable=True)
    queue_depth         = Column(Integer, nullable=True)
    utilization_pct     = Column(Float, nullable=True)
    overflow_redirects  = Column(Integer, default=0)


class WaitTimeTrend(Base):
    __tablename__  = "wait_time_trends"
    __table_args__ = {"schema": "analytics"}

    trend_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("organization.departments.department_id"), nullable=True)
    branch_id     = Column(UUID(as_uuid=True), ForeignKey("organization.branches.branch_id"), nullable=True)
    date          = Column(Date, default=date.today)
    hour_of_day   = Column(Integer, nullable=True)
    avg_wait_mins = Column(Float, nullable=True)
    min_wait_mins = Column(Float, nullable=True)
    max_wait_mins = Column(Float, nullable=True)
    sample_count  = Column(Integer, nullable=True)


# ================================================================
#  PYDANTIC SCHEMAS
# ================================================================

class UserAuthData(BaseModel):
    user_ref_id: Optional[str] = None   # auto-generated if omitted
    role: RoleEnum = RoleEnum.patient   # defaults to patient
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    class Config:
        from_attributes = True

class UserAuthResponse(BaseModel):
    auth_id: str
    username: str
    role: RoleEnum
    is_active: bool
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    role: str

class HospitalData(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    chain_name: Optional[str] = None
    country: Optional[str] = None
    class Config: from_attributes = True

class HospitalResponse(BaseModel):
    hospital_id: str
    name: str
    chain_name: Optional[str] = None
    country: Optional[str] = None
    is_active: bool
    class Config: from_attributes = True

class BranchData(BaseModel):
    hospital_id: str
    branch_name: str = Field(..., min_length=2, max_length=200)
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_capacity: int = 100
    class Config: from_attributes = True

class BranchResponse(BaseModel):
    branch_id: str
    hospital_id: str
    branch_name: str
    city: Optional[str] = None
    total_capacity: int
    current_load: float
    is_active: bool
    class Config: from_attributes = True

class DepartmentData(BaseModel):
    branch_id: str
    name: str = Field(..., min_length=2, max_length=200)
    specialty: Optional[str] = None
    floor_number: Optional[int] = None
    class Config: from_attributes = True

class DepartmentResponse(BaseModel):
    department_id: str
    branch_id: str
    name: str
    specialty: Optional[str] = None
    is_active: bool
    class Config: from_attributes = True

class PatientData(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    class Config: from_attributes = True

class PatientResponse(BaseModel):
    patient_id: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    class Config: from_attributes = True

class DoctorData(BaseModel):
    department_id: Optional[str] = None
    full_name: str = Field(..., min_length=2, max_length=200)
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_yrs: Optional[int] = None
    avg_consult_mins: float = 15.0
    phone: Optional[str] = None
    email: Optional[str] = None
    class Config: from_attributes = True

class DoctorResponse(BaseModel):
    doctor_id: str
    full_name: str
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_yrs: Optional[int] = None
    avg_consult_mins: float
    department_id: Optional[str] = None
    is_active: bool
    class Config: from_attributes = True

class AppointmentData(BaseModel):
    patient_id: str
    doctor_id: str
    branch_id: str
    slot_id: Optional[str] = None
    urgency_level: UrgencyEnum
    appointment_type: AppointmentTypeEnum
    scheduled_time: datetime
    notes: Optional[str] = None
    class Config: from_attributes = True

class AppointmentResponse(BaseModel):
    appointment_id: str
    patient_id: str
    doctor_id: str
    branch_id: str
    urgency_level: UrgencyEnum
    appointment_type: AppointmentTypeEnum
    status: AppointmentStatusEnum
    scheduled_time: datetime
    booked_at: Optional[datetime] = None
    notes: Optional[str] = None
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

class TimeSlotData(BaseModel):
    doctor_id: str
    branch_id: str
    date: date
    start_time: time
    end_time: time
    capacity: int = 1
    class Config: from_attributes = True

class TimeSlotResponse(BaseModel):
    slot_id: str
    doctor_id: str
    branch_id: str
    date: date
    start_time: time
    end_time: time
    is_available: bool
    is_peak_hour: bool
    booked_count: int
    class Config: from_attributes = True

class QueueEntryResponse(BaseModel):
    queue_id: str
    appointment_id: str
    doctor_id: str
    branch_id: str
    position: int
    estimated_wait_mins: Optional[int] = None
    is_emergency: bool
    status: QueueStatusEnum
    entered_queue_at: Optional[datetime] = None
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

class PriorityScoreResponse(BaseModel):
    score_id: str
    queue_id: str
    raw_urgency_score: Optional[int] = None
    raw_wait_score: Optional[float] = None
    raw_age_score: Optional[int] = None
    raw_type_score: Optional[int] = None
    final_score: float
    computed_at: Optional[datetime] = None
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

class EmergencyOverrideData(BaseModel):
    queue_id: str
    triggered_by: Optional[str] = None
    reason: str = Field(..., min_length=5)
    class Config: from_attributes = True

class EmergencyOverrideResponse(BaseModel):
    override_id: str
    queue_id: str
    reason: str
    previous_position: Optional[int] = None
    new_position: int
    triggered_at: Optional[datetime] = None
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
