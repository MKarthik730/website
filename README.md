<h3 align="left">📌 About this project</h3>
<p align="left">
  This repository contains a FastAPI-based user management API with SQLAlchemy ORM and a simple HTML dashboard. It demonstrates production-style CRUD operations on user data, database integration (SQLite/PostgreSQL), and basic WebSocket/TCP-style communication for experimentation.
</p>

<h3 align="left">📂 Repository Structure</h3>
<ul>
  <li><code>main.py</code> – FastAPI application entry point and API routes</li>
  <li><code>database.py</code> – Database engine and session configuration (SQLite/PostgreSQL)</li>
  <li><code>databasemodels.py</code> – SQLAlchemy models for user data</li>
  <li><code>functions.py</code> &amp; <code>data.py</code> – CRUD helpers and data utilities</li>
  <li><code>index.html</code> – Frontend dashboard for user CRUD and WebSocket echo terminal</li>
  <li><code>sockets.py</code>, <code>server01.py</code>, <code>client.py</code>, <code>client02.py</code>, <code>igris.py</code> – TCP/WebSocket server–client experiments</li>
  <li><code>requirements.txt</code> – Python dependencies</li>
  <li><code>test.db</code> – SQLite database for local development</li>
</ul>

<h3 align="left">☁️ Backend & Database</h3>
<p align="left">
  <a href="https://fastapi.tiangolo.com/" target="_blank" rel="noreferrer">
    <img src="https://cdn.worldvectorlogo.com/logos/fastapi.svg" alt="fastapi" width="40" height="40"/>
  </a>
  <a href="https://www.postgresql.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" alt="postgresql" width="40" height="40"/>
  </a>
</p>
