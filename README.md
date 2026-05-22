# 🛡️ Sentinel AI — Production Deployment Guide

This guide details the step-by-step procedure to deploy the **Sentinel AI Security platform** to production using **MongoDB Atlas**, **Render (Backend)**, and **Vercel (Frontend)**.

---

## 🏗️ Production Architecture

```mermaid
graph TD
    User([Browser Client]) -->|HTTPS| Frontend[Vercel SPA - React]
    User -->|API REST / JSON| Backend[Render - FastAPI App]
    Backend -->|Async Connection| Database[(MongoDB Atlas Cloud)]
    Backend -->|Optional Moderation| AI[OpenAI / Gemini APIs]
```

---

## 1. Cloud Database Setup (MongoDB Atlas)

To transition from a local MongoDB server to a high-availability cloud database:

1. **Sign Up**: Create an account on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. **Create Cluster**: Deploy a free tier cluster (`M0 Sandbox`) in your preferred region.
3. **Database User**:
   - Navigate to **Security > Database Access**.
   - Click **Add New Database User**.
   - Select **Read and write to any database** privileges.
   - Securely save the password.
4. **Network Access**:
   - Navigate to **Security > Network Access**.
   - Click **Add IP Address**.
   - Choose **Allow Access from Anywhere** (`0.0.0.0/0`) since Render's outbound IPs rotate dynamically.
5. **Connection String**:
   - Click **Connect** on the Database cluster.
   - Choose **Drivers** and copy the standard connection string:
     ```
     mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
     ```

---

## 2. Backend Deployment (Render)

Render hosts the FastAPI application inside an isolated Docker container or standard Python Web Service.

### Option A: Standard Web Service (Python)
1. **Import Repository**: Connect your GitHub/GitLab repository to Render.
2. **Select Web Service**: Select the `backend` subdirectory as the project root.
3. **Build & Start Settings**:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Define Env Variables**: Add variables in the **Environment** tab (see checklist below).

### Option B: Docker Container Service
Render can build your Dockerfile automatically:
- **Build Command**: Leave blank.
- **Start Command**: Leave blank (uses Dockerfile's standard `CMD`).
- Render detects `backend/Dockerfile` and deploys it natively.

---

## 3. Frontend Deployment (Vercel)

Vercel provides CDN distribution and global caching for static Single-Page Apps (SPAs).

1. **Import Project**: Select the `ai-fortress-frontend` directory.
2. **Framework Preset**: Choose **Vite** or **Other**.
3. **Build & Directory Settings**:
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. **Environment Variables**:
   - Key: `VITE_API_BASE_URL`
   - Value: `https://your-sentinel-backend.onrender.com/api/v1`
5. **Deploy**: Click **Deploy**. Vercel will build the bundles and host the app with clean URL fallbacks via the pre-configured `vercel.json`.

---

## 📋 Production Environment Variables

### Backend (`.env`)
| Variable Name | Production Description | Example/Fallback |
| :--- | :--- | :--- |
| `MONGODB_URI` | Connection string to MongoDB Atlas | `mongodb+srv://admin:pass@atlas...` |
| `DB_NAME` | Database schema name | `sentinel_ai` |
| `JWT_SECRET` | Cryptographically secure signature key | *Generate with `openssl rand -hex 32`* |
| `JWT_ALGORITHM` | Encryption algorithm | `HS256` |
| `JWT_EXPIRY_MINUTES` | Session duration (24h) | `1440` |
| `RATE_LIMIT_PER_MINUTE`| Maximum rate threshold | `60` |
| `ALLOWED_ORIGINS` | Comma-separated CORS values | `https://your-app.vercel.app` |
| `APP_ENV` | Target runtime environment | `production` |
| `USE_AI_MODERATION` | Toggle active cloud moderation | `true` |
| `AI_PROVIDER` | Selected service model | `openai` (or `gemini`, `local`) |
| `OPENAI_API_KEY` | Optional OpenAI credentials | `sk-proj-...` |
| `GEMINI_API_KEY` | Optional Gemini API key | `AIzaSy...` |

### Frontend (`.env`)
| Variable Name | Production Description | Example |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Live URL pointing to your Render gateway | `https://api.sentinel.app/api/v1` |

---

## 🐳 Self-Host Deployment (Docker Compose)

To orchestrate the full-stack infrastructure locally or on a VPS (AWS EC2, DigitalOcean Droplet):

1. **Start Stack**:
   ```bash
   docker-compose up -d --build
   ```
2. **Logs Verification**:
   ```bash
   docker-compose logs -f backend
   ```
3. **Clean Shutdown**:
   ```bash
   docker-compose down -v
   ```

---

## 🛠️ Deployment Troubleshooting Guide

### 1. Mixed Content Error (`Blocked loading mixed active content`)
- **Reason**: Your frontend is hosted on HTTPS (Vercel) but trying to connect to a non-secured HTTP API (`http://localhost:8000`).
- **Solution**: Always update your `VITE_API_BASE_URL` to the secure `https://` Render link before compiling the frontend.

### 2. CORS Blocked Errors (`No 'Access-Control-Allow-Origin' header present`)
- **Reason**: The backend rejected pre-flight API calls because the browser's origin isn't listed.
- **Solution**: Set `ALLOWED_ORIGINS` on Render's env variables dashboard to your exact Vercel address:
  `ALLOWED_ORIGINS=https://your-sentinel-app.vercel.app,http://localhost:5173`

### 3. Server Startup Timeout on Render
- **Reason**: Render free instances sleep after 15 minutes of inactivity, causing the initial load to experience a 30-50s cold-start spin-up latency.
- **Solution**: Configure a heartbeat cron job (e.g. [UptimeRobot](https://uptimerobot.com)) pointing to the `/health` endpoint to keep the container continuously warm, or upgrade to a paid web service plan.

### 4. MongoDB Authentication & Connection Retries
- **Reason**: Network security blocked connection or the password string has special characters not properly URL encoded.
- **Solution**: Use `urllib.parse.quote_plus` on passwords with symbols like `@`, `#`, or `/`, and verify that `0.0.0.0/0` is permitted under Atlas Network security rules.
