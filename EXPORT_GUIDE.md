# JobHunt - Project Export & Setup Guide

A complete, self-contained guide for exporting, setting up, and running the **JobHunt** system on any new machine or environment.

---

## 📌 Project Overview

**JobHunt** is an AI-powered job search aggregator, pre-screening, and candidate matching application designed for the Israeli job market. It collects job postings from multiple platforms, pre-filters them based on customizable criteria, scores their compatibility against a user's CV using Google Gemini AI, and provides a modern web portal and Chrome extension for live LinkedIn sync.

### Key Components

1. **FastAPI Backend (`/backend`)**: Manages SQLite storage, web scrapers (Drushim, JobMaster, Secret Tel Aviv, GotFriends, Goozali), REST API endpoints, candidate CV parsing, pre-screening logic, and Gemini AI matching.
2. **React Frontend (`/frontend`)**: A high-performance Vite + React 19 web dashboard with score filtering, RTL (Hebrew/English) support, match reasoning breakdowns, and settings management.
3. **LinkedIn Sync Extension (`/linkedin-extension`)**: A Manifest V3 Chrome Extension that automates job extraction from logged-in LinkedIn search results with auto-pagination and remote logging to the local backend.

---

## 📁 Repository Structure

```text
JobHunt/
├── backend/
│   ├── main.py              # FastAPI app routes & API endpoints (/api/jobs, /api/settings, /api/logs, etc.)
│   ├── database.py          # SQLite connection and database schema manager (jobhunt.db)
│   ├── scraper.py           # Multi-platform scrapers (Drushim, JobMaster, Secret Tel Aviv, GotFriends, Goozali)
│   ├── pre_filter.py        # Must-have & exclusion keyword screening logic
│   ├── matching_agent.py    # AI candidate match scoring engine via Gemini API
│   ├── cv_optimizer.py      # Candidate CV optimization suggestions
│   ├── pdf_parser.py        # PDF CV text parser
│   ├── requirements.txt     # Python dependency list
│   └── jobhunt.db           # SQLite database file storing jobs, match scores, & settings
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI components (JobCard, FilterBar, SettingsModal, etc.)
│   │   ├── App.jsx          # Main dashboard page logic
│   │   ├── index.css        # Global CSS design system & dynamic tokens
│   │   └── main.jsx         # React application entry point
│   ├── package.json         # Node.js dependencies and scripts
│   └── vite.config.js       # Vite configuration
├── linkedin-extension/
│   ├── manifest.json        # Chrome Extension Manifest V3 specification
│   ├── content.js           # Page automation, Shadow DOM DOM traversal, & multi-page scan loop
│   ├── popup.html           # Extension popup UI layout
│   └── popup.js             # Popup controller & backend health check
├── Pini_Matzner_2026.pdf    # Sample candidate CV PDF
└── EXPORT_GUIDE.md          # This export & setup guide
```

---

## 🛠️ Prerequisites

Ensure the following tools are installed on your target machine:

* **Python**: `3.10` or higher
* **Node.js**: `18.0.0` or higher (with `npm`)
* **Google Chrome**: Needed for running the LinkedIn Sync Chrome Extension
* **Gemini API Key**: Required for AI matching (`GEMINI_API_KEY` environment variable)

---

## 🚀 Quick Setup Instructions

### 1. Export / Copy Project Files

Copy or clone the entire `JobHunt` workspace folder to the destination environment:

```bash
git clone https://github.com/PiniMatz/JobHunt.git
cd JobHunt
```

---

### 2. Backend Setup (FastAPI + Python)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   * **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set your **Gemini API Key**:
   * **Windows (PowerShell)**:
     ```powershell
     $env:GEMINI_API_KEY="your-gemini-api-key-here"
     ```
   * **Linux / macOS**:
     ```bash
     export GEMINI_API_KEY="your-gemini-api-key-here"
     ```

5. Start the FastAPI backend server:
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
   * The API will run at: `http://127.0.0.1:8000`
   * API Documentation (Swagger): `http://127.0.0.1:8000/docs`

---

### 3. Frontend Setup (React + Vite)

1. Open a new terminal tab/window and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install Node packages:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to the printed local URL (typically `http://localhost:5173` or `http://localhost:5174`).

---

### 4. LinkedIn Extension Setup (Chrome)

To enable live job scanning from LinkedIn:

1. Open **Google Chrome** and navigate to `chrome://extensions/`.
2. Toggle **Developer mode** on in the top-right corner.
3. Click **Load unpacked** in the top-left corner.
4. Select the `linkedin-extension` folder inside your project directory.
5. Log into [LinkedIn](https://www.linkedin.com/) in Chrome and run any job search (e.g. "Product Manager in Israel").
6. Click the **JobHunt Sync** extension icon in your Chrome toolbar and click **Scan Current Search Page 🚀**.

---

## 🗄️ Database & Migration Notes

* **Database Engine**: SQLite (`backend/jobhunt.db`).
* **Portability**: To transfer your existing collected jobs, match scores, and settings, simply copy the `jobhunt.db` file alongside the backend code.
* **Auto Initialization**: If `jobhunt.db` does not exist on first launch, `database.py` will automatically create the tables and set default initial values.

---

## 🔑 Key Backend Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/jobs` | `GET` | Retrieve collected jobs with match scores and status filters |
| `/api/scan` | `POST` | Trigger background web scraping across Israeli job sites |
| `/api/jobs/import` | `POST` | Endpoint receiving job payloads from the Chrome Extension |
| `/api/logs` | `POST` | Receives live remote extension diagnostic logs |
| `/api/settings` | `GET / POST` | Read or update must-haves, exclusion keywords, & target roles |
| `/api/upload-cv` | `POST` | Upload and parse candidate PDF resume |

---

## ⚙️ Configuration & Customization

* **Port Collisions**: If port `5173` is busy, Vite will automatically select `5174`. The backend CORS origin allows all local origins by default.
* **Scraper Adjustments**: Target job site scrapers can be tuned or extended in `backend/scraper.py`.
* **Keyword Rules**: Must-have and exclusion keyword lists can be updated directly via the UI **Settings** modal or through `backend/pre_filter.py`.

---

*Created for JobHunt project export and environment migration.*
