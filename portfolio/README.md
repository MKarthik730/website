<<<<<<< HEAD
# Portfolio Website

A modern, responsive portfolio website showcasing my projects and skills.

## Features

- Responsive design that works on all devices
- Smooth scrolling navigation
- Animated statistics counter
- Project showcase with GitHub links
- Skills and technologies display
- Contact links to GitHub and LinkedIn

## Technologies Used

- HTML5
- CSS3 (with CSS Grid and Flexbox)
- Vanilla JavaScript
- Font Awesome Icons

## How to View the Portfolio Website

### Option 1: Open Directly (Quick Start)
- Double-click `run_portfolio.bat` - This will open `index.html` in your default browser
- Or manually right-click `index.html` and select "Open with" your preferred browser

### Option 2: Using Local Web Server (Recommended)
For best results and to avoid any CORS issues:

**Windows:**
- Double-click `run_server.bat` - This starts a Python web server
- Then open http://localhost:8000 in your browser

**Manual Command:**
```bash
# Navigate to portfolio folder
cd portfolio

# Using Python
python -m http.server 8000

# Or using Node.js (if http-server is installed)
npx http-server -p 8000
```

Then open http://localhost:8000 in your browser.

### Option 3: GitHub Pages (Online Hosting)
To host your portfolio online for free:
1. Go to your GitHub repository: https://github.com/MKarthik730/website
2. Click on "Settings" tab
3. Scroll down to "Pages" section
4. Under "Source", select "Deploy from a branch"
5. Choose "main" branch and "/portfolio" folder
6. Click "Save"
7. Your portfolio will be live at: `https://mkarthik730.github.io/website/portfolio/`

## Files

- `index.html` - Main HTML structure
- `style.css` - All styling and responsive design
- `script.js` - JavaScript for interactivity and animations
- `run_portfolio.bat` - Quick launcher to open portfolio in browser
- `run_server.bat` - Launcher to start local web server
- `README.md` - This file

## Customization

To customize the portfolio with your own information:

1. Update personal details in `index.html`
2. Modify project information in the projects section
3. Adjust skills in the skills section
4. Change colors in `style.css` using CSS variables
5. Update social media links
=======
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
>>>>>>> 18fa72778c9b8e3c9ab0bae9b6a17240c49d74f2
