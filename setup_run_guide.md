# 🛠️ Sentinel AI — Developer Run, Debug & Startup Playbook

Welcome to the team! As a senior DevOps and platform engineer, I have structured this playbook to guide you through setting up, configuring, launching, and debugging the entire **Sentinel AI Full-Stack Platform** on your local machine.

---

## 📂 Project Architecture Overview

Your workspace has two primary directories representing a standard microservices-style decoupled application:
```
layer app and llm/                  # Workspace Root
├── ai-fortress-frontend/           # React + Vite + TanStack Client App
│   ├── src/                        # React source files
│   ├── .env                        # Local client environment file
│   └── package.json                # Node package declarations
├── backend/                        # FastAPI + Motor (MongoDB Async) Gateway
│   ├── app/                        # Python application logic
│   ├── main.py                     # API entry point (Lifespan + CORS + Routes)
│   ├── .env                        # Local backend environment file
│   └── requirements.txt            # Python pip dependencies
├── docker-compose.yml              # Single-command self-hosted engine
└── README.md                       # Production deployment handbook
```

---

## 💾 1. Database Setup (MongoDB)

Sentinel AI requires a MongoDB database instance to store users, historical scan records, and active threat catalogs. You can choose either **Local Installation** or **MongoDB Atlas Cloud**.

### Option A: Local MongoDB Community Server (Recommended for offline development)
1. **Download**: Visit [MongoDB Community Downloads](https://www.mongodb.com/try/download/community) and download the MSI installer for Windows.
2. **Install**: Run the installer. Ensure you check **Install MongoDB as a Service** and **Install MongoDB Compass** (a graphical user interface for browsing documents).
3. **Verify Service status**:
   - Open PowerShell as Administrator.
   - Run: `Get-Service -Name MongoDB` (should show `Running`).
4. **Local URI**: `mongodb://localhost:27017`

### Option B: Cloud MongoDB Atlas
1. Follow the **MongoDB Atlas Setup Guide** in the `README.md` to create a free sandbox.
2. Whitelist access from anywhere (`0.0.0.0/0`) during development.
3. **Atlas URI**: `mongodb+srv://<username>:<password>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0`

---

## 🐍 2. Backend Setup & Run

Open a **fresh terminal window** (e.g. Command Prompt or PowerShell) and execute these exact commands.

### Step 2.1: Navigate and Initialize Virtual Environment
Navigate to the backend directory and create an isolated Python virtual environment to prevent package version conflicts with other globally installed python libraries:
```powershell
# 1. Move into the backend project directory
cd "c:\Users\devyt\OneDrive\Documents\layer app and llm\backend"

# 2. Initialize a local virtual environment named 'venv'
python -m venv venv

# 3. Activate the environment (based on your shell)
# For PowerShell:
.\venv\Scripts\Activate.ps1
# For Windows CMD:
.\venv\Scripts\activate.bat
```
*(You will see `(venv)` prepended to your command line, indicating activation is successful.)*

### Step 2.2: Upgrade Package Managers & Install Requirements
```powershell
# 1. Upgrade pip to the latest release
python -m pip install --upgrade pip

# 2. Install all core libraries (FastAPI, Motor, Pydantic, httpx, jose)
pip install -r requirements.txt
```

### Step 2.3: Establish Environment Variable Configuration
Check if your `.env` is setup. If not, copy it from `.env.example`:
```powershell
copy .env.example .env
```
Ensure your `.env` contains the correct connection values:
```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=sentinel_ai
JWT_SECRET=sentinel-dev-secret-key-2026-change-in-prod
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=1440
RATE_LIMIT_PER_MINUTE=60
API_VERSION=v1
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
USE_AI_MODERATION=true
AI_PROVIDER=local
```

### Step 2.4: Launch the FastAPI Gateway Server
```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
You should see:
```
INFO:     Started server process [12884]
INFO:     Waiting for application startup.
INFO:     Starting Sentinel AI v1.0.0 ...
INFO:     Connected to MongoDB successfully!
INFO:     Database threat definition catalog synchronized.
INFO:     Sentinel AI is ready. Environment: development
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## ⚡ 3. Frontend Setup & Run

Open a **second fresh terminal window** to host your Vite development server.

### Step 3.1: Navigate and Configure Dependencies
Navigate into the React project directory:
```powershell
# 1. Move into the frontend project directory
cd "c:\Users\devyt\OneDrive\Documents\layer app and llm\ai-fortress-frontend"

# 2. Install Node packages safely bypassing possible legacy dependency conflicts
npm install --legacy-peer-deps
```

### Step 3.2: Establish Environment Variable Configuration
Confirm that you have a `.env` file pointing directly to your backend API Gateway:
```powershell
# In ai-fortress-frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Step 3.3: Run the Vite Local Dev Server
```powershell
npm run dev
```
Vite will output:
```
  VITE v7.3.3  ready in 218 ms
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```
Hold `Ctrl` and click `http://localhost:5173/` to open the console dashboard.

---

## 🛠️ Senior DevOps Debugging Manual

If you encounter any glitches or environment hurdles, find the exact resolution recipe below:

### 🚨 1. CORS Pre-Flight Block (`Access-Control-Allow-Origin` error)
- **Symptom**: Browser Console displays a CORS failure indicating headers are missing from `/scan` or `/login`.
- **Diagnosis**: The frontend origin (`http://localhost:5173`) does not match the backend's `ALLOWED_ORIGINS`.
- **Resolution**:
  1. Open `backend/.env`.
  2. Verify `ALLOWED_ORIGINS` has no trailing slashes: `ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000`.
  3. Restart the Uvicorn terminal process (`Ctrl+C` and run the command again).

### 🚨 2. MongoDB Handshake Failure (`ServerSelectionTimeoutError`)
- **Symptom**: Backend startup crashes with a timeout connecting to `localhost:27017` or Atlas.
- **Diagnosis**: Local MongoDB Service is stopped, or Atlas IP Whitelist is blocking Render/your local network.
- **Resolution**:
  - **Local Fix**: Search for `Services` in Windows search. Find **MongoDB Server**, right-click it, and choose **Start**.
  - **Cloud Atlas Fix**: Access MongoDB Atlas Panel > Network Access > click **Edit** and set IP to `0.0.0.0/0` (Allow all).

### 🚨 3. Python Virtualenv Script Execution Block (Windows PowerShell Policy)
- **Symptom**: Activating `venv` outputs: `Script cannot be loaded because running scripts is disabled on this system`.
- **Diagnosis**: Windows client execution policies are preventing custom shell script triggers.
- **Resolution**:
  - Run PowerShell as **Administrator** and execute:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
    ```
  - Re-run the activation script: `.\venv\Scripts\Activate.ps1`.

### 🚨 4. JWT Authorization / Invalid Credentials Faults
- **Symptom**: Logins fail or requests constantly return a 401 unauthenticated redirect loop.
- **Diagnosis**:
  - Client token is corrupted in `localStorage`.
  - Backend `JWT_SECRET` changed or doesn't match current active sessions.
- **Resolution**:
  - Open Developer Console in your browser (`F12`), head to **Application > Local Storage**, right-click, and click **Clear** (to clean cookies/tokens), then refresh the login screen.

### 🚨 5. React Node Modules Build Conflicts (`esbuild` / Types Errors)
- **Symptom**: `npm run dev` fails with package resolution or compiler issues.
- **Diagnosis**: Outdated/incompatible modules in Node tree.
- **Resolution**:
  - Clear build caches and perform a clean install:
    ```powershell
    Remove-Item -Recurse -Force node_modules, package-lock.json
    npm install --legacy-peer-deps
    ```
