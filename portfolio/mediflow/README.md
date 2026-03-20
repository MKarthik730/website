# MediFlow 🏥

> A full-stack hospital management system with intelligent queue management, doctor load balancing, and appointment analytics — built with FastAPI and vanilla JS.

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

---

## What is MediFlow?

MediFlow is a hospital management system that handles the full patient lifecycle — from booking appointments to doctor queue management. The core feature is an algorithm-driven load balancer that distributes patients across doctors based on availability, specialization, and predicted peak hours, reducing wait times and preventing doctor overload.

---

## Features

### Patient & Doctor Management
- Patient registration, profile management, and medical history
- Doctor profiles with specialization, branch assignment, and slot availability
- Admin dashboard for managing hospital branches and staff

### Smart Appointment System
- Slot-based appointment booking with real-time availability
- **Queue management** — patients are ordered by priority and arrival
- **Doctor load balancing** — algorithm distributes incoming appointments to prevent any single doctor from being overloaded
- **Peak hour prediction** — analyzes historical booking patterns to forecast busy periods

### Analytics & Reporting
- Appointment volume trends by branch and doctor
- Peak hour heatmaps for operational planning
- Patient throughput and wait time metrics

### Auth & Access Control
- JWT-based user authentication
- Role-based access: Admin / Doctor / Patient

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL, SQLAlchemy ORM |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Auth | JWT tokens |
| Algorithms | Custom load balancing, peak prediction |

---

## Project Structure

```
mediflow/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── auth.py              # Login, register, JWT
│   │   ├── patients.py          # Patient CRUD
│   │   ├── doctors.py           # Doctor management
│   │   ├── appointments.py      # Booking and queue endpoints
│   │   └── analytics.py         # Reporting endpoints
│   ├── algorithms/
│   │   ├── load_balancer.py     # Doctor assignment logic
│   │   └── peak_predictor.py    # Appointment volume forecasting
│   └── models/                  # SQLAlchemy ORM models
├── frontend/
│   ├── index.html               # Landing / login page
│   ├── dashboard/               # Admin and doctor dashboards
│   └── patient/                 # Patient booking flow
└── mediflow_db/
    ├── config.py                # DB connection settings
    └── init.py                  # Schema initialization
```

---

## Load Balancing Algorithm

When a patient books an appointment, the system doesn't just pick any available doctor. It scores each eligible doctor using:

```
score = w1 * (1 / current_queue_length)
      + w2 * specialization_match
      + w3 * (1 / predicted_load_at_slot)
```

The doctor with the highest score gets assigned. This keeps queues balanced across the day without manual admin intervention.

---

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL running locally

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Configure your database in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/mediflow_db
SECRET_KEY=your_jwt_secret
```

Initialize the database and run:
```bash
python mediflow_db/init.py
uvicorn main:app --reload
```

API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
# Open index.html directly in browser
# Or serve locally:
python -m http.server 3000
```

Open `http://localhost:3000`

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/doctors` | List doctors with availability |
| POST | `/appointments` | Book appointment (triggers load balancer) |
| GET | `/appointments/{id}` | Get appointment + queue position |
| GET | `/analytics/peaks` | Peak hour prediction data |
| GET | `/analytics/load` | Doctor load distribution |

---

## What I Learned

- Designing normalized relational schemas for complex scheduling data (slots, branches, doctors, patients all interconnected)
- Implementing a weighted scoring algorithm for resource allocation — similar to how real hospital EMR systems work
- FastAPI's dependency injection pattern for clean auth middleware
- Why predicting load matters in scheduling systems — greedy "first available" assignment creates uneven queues

---

## Roadmap

- [ ] SMS/email notifications for appointment reminders
- [ ] Real-time queue updates via WebSocket
- [ ] Mobile-responsive frontend
- [ ] Docker Compose setup for one-command deployment

---

## Author

**Karthik Motupalli** — [@MKarthik730](https://github.com/MKarthik730)  
CS Student, ANITS Vizag | [LinkedIn](https://www.linkedin.com/in/karthik-motupalli-0b6951318)
