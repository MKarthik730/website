# ================================================================
#  routers/analytics_router.py — FIXED: UUID branch/dept IDs
# ================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
import uuid

from mediflow_db.config import get_db
from mediflow_db.models import (
    AppointmentLog, PeakHourStat, DoctorPerformance,
    BranchLoadStat, WaitTimeTrend, Appointment,
)
from auth import require_role
from algorithms.peak_prediction import train_forecaster, get_forecaster

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


def _try_uuid(val):
    try: return uuid.UUID(str(val))
    except (ValueError, TypeError): return None


@router.get("/summary")
def admin_summary(db: Session = Depends(get_db), _: dict = Depends(require_role("admin", "staff"))):
    today = date.today()
    total_today = db.query(Appointment).filter(Appointment.scheduled_time >= today).count()
    completed   = db.query(Appointment).filter(Appointment.status == "completed").count()
    cancelled   = db.query(Appointment).filter(Appointment.status == "cancelled").count()
    emergency   = db.query(Appointment).filter(Appointment.urgency_level == "critical").count()
    return {"appointments_today": total_today, "total_completed": completed,
            "total_cancelled": cancelled, "critical_cases": emergency}


@router.get("/peak-forecast")
def peak_forecast(branch_id: str, department_id: str, db: Session = Depends(get_db),
                  _: dict = Depends(require_role("admin", "staff"))):
    b_id = _try_uuid(branch_id)
    stats = (db.query(PeakHourStat)
             .filter(PeakHourStat.branch_id == b_id)
             .order_by(PeakHourStat.recorded_on, PeakHourStat.hour_of_day)
             .all()) if b_id else []
    history = [s.avg_appointments or 0.0 for s in stats]
    if len(history) < 4:
        return {"message": "Not enough historical data", "forecast": []}
    forecast = train_forecaster(branch_id, department_id, history)
    hw       = get_forecaster(branch_id, department_id)
    peaks    = hw.peak_hours(24, top_n=3)
    return {"branch_id": branch_id, "department_id": department_id,
            "forecast_24h": forecast, "peak_hours": peaks, "data_points": len(history)}


@router.get("/appointment-density")
def appointment_density(branch_id: str, days: int = 7, db: Session = Depends(get_db),
                        _: dict = Depends(require_role("admin", "staff"))):
    b_id  = _try_uuid(branch_id)
    since = date.today() - timedelta(days=days)
    logs  = (db.query(AppointmentLog)
             .filter(AppointmentLog.branch_id == b_id, AppointmentLog.scheduled_time >= since)
             .all()) if b_id else []
    density = {}
    for log in logs:
        if log.scheduled_time:
            key = f"{log.scheduled_time.strftime('%A')}_{log.scheduled_time.hour:02d}"
            density[key] = density.get(key, 0) + 1
    return {"branch_id": branch_id, "density": density}


@router.get("/wait-time-trends")
def wait_time_trends(department_id: str, days: int = 14, db: Session = Depends(get_db),
                     _: dict = Depends(require_role("admin", "staff"))):
    d_id  = _try_uuid(department_id)
    since = date.today() - timedelta(days=days)
    trends = (db.query(WaitTimeTrend)
              .filter(WaitTimeTrend.department_id == d_id, WaitTimeTrend.date >= since)
              .order_by(WaitTimeTrend.date, WaitTimeTrend.hour_of_day)
              .all()) if d_id else []
    return [{"date": str(t.date), "hour": t.hour_of_day, "avg_wait_mins": t.avg_wait_mins,
             "min_wait_mins": t.min_wait_mins, "max_wait_mins": t.max_wait_mins,
             "sample_count": t.sample_count} for t in trends]


@router.get("/doctor-performance")
def doctor_performance(doctor_id: str, days: int = 30, db: Session = Depends(get_db),
                       _: dict = Depends(require_role("admin", "staff"))):
    d_id  = _try_uuid(doctor_id)
    since = date.today() - timedelta(days=days)
    records = (db.query(DoctorPerformance)
               .filter(DoctorPerformance.doctor_id == d_id, DoctorPerformance.date >= since)
               .order_by(DoctorPerformance.date)
               .all()) if d_id else []
    return [{"date": str(r.date), "total_appointments": r.total_appointments,
             "completed_count": r.completed_count, "no_show_count": r.no_show_count,
             "avg_consult_mins": r.avg_consult_mins, "avg_wait_mins": r.avg_wait_mins,
             "utilization_pct": r.utilization_pct} for r in records]


@router.get("/branch-load-history")
def branch_load_history(branch_id: str, hours: int = 24, db: Session = Depends(get_db),
                        _: dict = Depends(require_role("admin", "staff"))):
    from datetime import datetime, timedelta as td
    b_id  = _try_uuid(branch_id)
    since = datetime.utcnow() - td(hours=hours)
    stats = (db.query(BranchLoadStat)
             .filter(BranchLoadStat.branch_id == b_id, BranchLoadStat.recorded_at >= since)
             .order_by(BranchLoadStat.recorded_at)
             .all()) if b_id else []
    return [{"recorded_at": s.recorded_at.isoformat(), "active_appointments": s.active_appointments,
             "queue_depth": s.queue_depth, "utilization_pct": s.utilization_pct,
             "overflow_redirects": s.overflow_redirects} for s in stats]
