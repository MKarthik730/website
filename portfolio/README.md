# Website - Learning Web Technology

A collection of projects built while learning full-stack web development with Python, FastAPI, and modern frontend technologies.

---

## Tech Stack

### Frontend
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

### Backend
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

### Database
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

### Tools & Libraries
[![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MKarthik730)
[![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/)
[![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![Axios](https://img.shields.io/badge/Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white)](https://axios-http.com/)

---

## Repository Structure

```
website/
│
├── backend/                        # FastAPI practice server
│   ├── igris.py
│   ├── main.py
│   ├── server01.py
│   └── sockets.py
│
├── crimson/                        # Hospital Management System
│   ├── backend/
│   │   ├── algorithms/             # Core scheduling algorithms
│   │   │   ├── bipartite_matching.py
│   │   │   ├── interval_tree.py
│   │   │   ├── kdtree.py
│   │   │   ├── load_balancer.py
│   │   │   ├── peak_prediction.py
│   │   │   ├── priority_queue.py
│   │   │   └── wait_time.py
│   │   ├── mediflow_db/            # Database layer
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── init_db.py
│   │   │   ├── models.py
│   │   │   └── schemas_pg.sql
│   │   ├── routers/                # API route handlers
│   │   │   ├── analytics_router.py
│   │   │   ├── appointment_router.py
│   │   │   ├── auth_router.py
│   │   │   ├── branch_router.py
│   │   │   ├── doctor_router.py
│   │   │   ├── patient_router.py
│   │   │   ├── queue_router.py
│   │   │   └── slot_router.py
│   │   ├── auth.py
│   │   ├── create_admin.py
│   │   └── main.py
│   ├── frontend/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   └── pages.js
│   │   └── index.html
│   └── models/
│       ├── analytics.py
│       ├── organization.py
│       ├── queue.py
│       ├── scheduling.py
│       └── users.py
│
├── database/                       # Database utilities
│   ├── data.py
│   ├── database.py
│   └── databasemodels.py
│
├── fastapi/                        # FastAPI learning notes & examples
│   ├── learn/
│   │   ├── api_01.py
│   │   └── user_from.py
│   ├── 01_ULTIMATE_FASTAPI_TUTORIAL.md
│   ├── 02_ADVANCED_PRODUCTION_APP.py
│   ├── 03_COMPREHENSIVE_TESTS.py
│   ├── 04_DEPLOYMENT_GUIDE.md
│   └── 05_ADVANCED_REFERENCE.md
│
├── frontend/                       # Frontend client
│   ├── client.py
│   └── index.html
│
├── portfolio/                      # Personal portfolio site
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── profile.jpeg
│
├── storage-web/                    # File storage web app
│   ├── backend/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── uploads/
│   │       ├── documents/
│   │       └── images/
│   ├── database/
│   │   ├── database.py
│   │   └── models.py
│   ├── frontend/
│   │   └── app.py
│   └── requirements.txt
│
├── functions.py
├── index.html
├── script.js
├── style.css
├── requirements.txt
└── README.md
```

---

## Projects

**Crimson - Hospital Management System** — Full-stack app with patient management, doctor scheduling, queue management, and analytics powered by FastAPI and PostgreSQL.

**Storage Web** — File upload and storage web application with document and image management.

**Portfolio** — Personal portfolio website built with HTML, CSS, and JavaScript.

**FastAPI Learning** — Study notes, tutorials, and practice code for learning FastAPI.

---

## Getting Started

**Backend (Crimson)**
```bash
cd crimson/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Storage Web**
```bash
cd storage-web
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

**Frontend**

Open `index.html` directly in your browser or serve on port 3000.

---

## Author

**Karthik** — [MKarthik730](https://github.com/MKarthik730)
