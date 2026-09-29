# CyberGuard: Memory-Powered AI Incident Response Agent
> **Track:** Vectorize Hindsight Memory Track  
> **Framework:** Hindsight Memory + Groq Fast LLM Inference + FastAPI Backend + Next.js Frontend

---

## Quick Start Guide

### 1. Start the Backend API Server
Navigate to the `backend` directory and run uvicorn pointing to `app.main:app`:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
> **Note:** If running uvicorn directly from the `backend/` folder, use `app.main:app`. If running from the repository root, use `backend.app.main:app`.

The API will be live at `http://localhost:8000`. You can view interactive API docs at `http://localhost:8000/docs`.

### 2. Start the Frontend SOC Dashboard
Open a second terminal, navigate to `frontend`, and start Next.js:

```bash
cd frontend
npm run dev
```
Open your browser at `http://localhost:3000`.

---

## 60-Second Demo Script for Judges

1. **Cold Start:** Select an attack vector or type raw syslog text $\rightarrow$ Click **Submit Alert**. Notice the initial baseline recommendation.
2. **Analyst Action Feedback:** Click **Mark as Worked** or **Mark as Failed**. Notice the real-time state tag `"Hindsight Memory Updated"`.
3. **Hot Recall:** Submit a similar alert $\rightarrow$ Watch CyberGuard recall past incident outcomes, bump Bayesian confidence to $> 90\%$, and warn against failed response strategies!
