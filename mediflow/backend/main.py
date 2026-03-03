# ================================================================
#  main.py — MediFlow FastAPI Application Entry Point
# ================================================================

# IMPORTANT: auth.py must be imported first — it patches bcrypt
# before passlib initialises its CryptContext.
import auth  # noqa: F401 — bcrypt patch applied here

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from mediflow_db.config import Base, engine, SessionLocal
import mediflow_db.models  # noqa: F401 — registers all ORM classes with Base

from algorithms.load_balancer import get_load_balancer
from algorithms.kdtree import rebuild_kdtree

from routers.auth_router        import router as auth_router
from routers.patient_router     import router as patient_router
from routers.doctor_router      import router as doctor_router
from routers.appointment_router import router as appointment_router
from routers.queue_router       import router as queue_router
from routers.slot_router        import router as slot_router
from routers.branch_router      import router as branch_router
from routers.analytics_router   import router as analytics_router


def create_schemas():
    schemas = ["organization", "users", "scheduling", "queue", "analytics"]
    raw_conn = engine.raw_connection()
    try:
        raw_conn.autocommit = True
        cur = raw_conn.cursor()
        for schema in schemas:
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
            print(f"  ✔ Schema '{schema}' ready")
        cur.close()
    finally:
        raw_conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🏥  MediFlow starting up…\n")

    print("📂  Creating PostgreSQL schemas…")
    create_schemas()

    print("\n🗄   Creating tables…")
    print(f"  Registered models: {len(Base.metadata.tables)}")
    Base.metadata.create_all(bind=engine)
    print("  ✔ All tables ready")

    # Seed in-memory data structures
    db = SessionLocal()
    try:
        from mediflow_db.models import Branch, UserAuth, RoleEnum
        branches = db.query(Branch).filter(Branch.is_active == True).all()
        lb = get_load_balancer()
        for b in branches:
            lb.register(str(b.branch_id), b.total_capacity)
            lb.update_load(str(b.branch_id), int((b.current_load or 0) * b.total_capacity))

        rebuild_kdtree([{
            "branch_id": str(b.branch_id),
            "latitude":  b.latitude  or 0.0,
            "longitude": b.longitude or 0.0,
            "is_active": b.is_active,
        } for b in branches])
        print(f"  ✔ Load balancer + K-d tree seeded ({len(branches)} branches)")

        # ── Admin check: warn loudly if no admin account exists ──
        admin_exists = db.query(UserAuth).filter(UserAuth.role == RoleEnum.admin).first()
        if not admin_exists:
            print("\n" + "="*60)
            print("  ⚠️  NO ADMIN ACCOUNT EXISTS")
            print("  Create one via the UI 'First Admin' tab, OR run:")
            print("  python create_admin.py")
            print("="*60 + "\n")
        else:
            print(f"  ✔ Admin account found: '{admin_exists.username}'")

    finally:
        db.close()

    print("\n✅  MediFlow ready → http://localhost:8000\n")
    yield
    print("🛑  MediFlow shutting down…")


app = FastAPI(
    title       = "MediFlow — Intelligent Healthcare Scheduling API",
    description = "Priority queue · Interval Tree · Hopcroft-Karp · Holt-Winters · Little's Law · K-d Tree",
    version     = "1.0.0",
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(appointment_router)
app.include_router(queue_router)
app.include_router(slot_router)
app.include_router(branch_router)
app.include_router(analytics_router)


@app.get("/", tags=["Health"])
def root():
    return {"service": "MediFlow API", "status": "running", "version": "1.0.0", "docs": "/docs"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
