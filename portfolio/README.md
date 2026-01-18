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
