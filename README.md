# SignalFlow

An Indian-stock prediction app: search the full NSE universe, build a watchlist,
view price history, and generate LSTM-based price forecasts. Django REST backend
with automated, scheduled model training (Celery) and a React frontend.

## Tech stack

- **Backend:** Django + Django REST Framework, PostgreSQL, JWT auth (SimpleJWT)
- **ML:** TensorFlow/Keras LSTM, scikit-learn, pandas; data from Yahoo Finance (yfinance)
- **Async/scheduling:** Celery + Redis (broker, result backend, cache), Celery Beat
- **Frontend:** Vite + React 19 + TypeScript, Tailwind + shadcn/ui, React Query, Recharts

## Features

- Email/JWT auth (register, login, token refresh, protected routes)
- Stock search across the full NSE equity list, with fuzzy (typo-tolerant) suggestions
- Watchlist (add/remove)
- Stock detail: 1-year price history + 30-day forecast overlay (Recharts)
- On-demand model training (async) and a daily 08:30 IST auto-retrain
- Training-run history with drift detection

## Project layout

```
backend-drf/    Django project (API, ML pipeline, Celery tasks)
frontend/       Vite + React app
```

---

## Prerequisites

- **Python 3.12+** with the project virtualenv at `backend-drf/.venv`
- **PostgreSQL** running locally (database `signalflow_db` on `localhost:5432`)
- **Redis** — required only for model training / scheduled retrain
- **Node.js 20+** — for the frontend

> On this machine Node is a portable install and Redis is a portable build; see the
> commands below.

## One-time setup

```powershell
# Backend
Set-Location backend-drf
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_nse_stocks      # load ~2000 NSE stocks
.\.venv\Scripts\python.exe manage.py createsuperuser      # optional, for /admin

# Frontend
$env:Path = "$env:USERPROFILE\nodejs-portable\node-v24.18.0-win-x64;$env:Path"
Set-Location ..\frontend
npm install
```

Configuration is via environment variables (see `backend-drf/.env.example` and
`frontend/.env.example`). Sensible localhost defaults are used when unset, but
`DJANGO_SECRET_KEY` is required when `DJANGO_DEBUG=False`.

---

## Running locally

Start each long-running process in **its own terminal**, in this order. Redis and
the Celery worker are only needed if you want to train models.

```powershell
# 1. Redis (portable build) — needed for training
& "$env:USERPROFILE\redis-portable\redis-server.exe"
#    verify:  & "$env:USERPROFILE\redis-portable\redis-cli.exe" ping   -> PONG



# 2. Celery worker (from backend-drf) — needed for training.
#    --pool=solo is REQUIRED on Windows.
celery -A stock_prediction_main worker -l info --pool=solo

# 3. Celery Beat (optional) — only for the daily 08:30 IST auto-retrain
celery -A stock_prediction_main beat -l info

# 4. Django API (from backend-drf)
python manage.py runserver          # http://localhost:8000

# 5. Frontend (from frontend)
$env:Path = "$env:USERPROFILE\nodejs-portable\node-v24.18.0-win-x64;$env:Path"
npm run dev                                             # http://localhost:5173
```

**Rule of thumb:** Redis → worker → Django → frontend.

### What you need for which task

| Task | Postgres | Django | Frontend | Redis | Celery worker |
|------|:---:|:---:|:---:|:---:|:---:|
| Browse, search, watchlist, charts, view predictions | ✅ | ✅ | ✅ | – | – |
| Train a model (Train button / `POST /ml/train/<ticker>/`) | ✅ | ✅ | ✅ | ✅ | ✅ |

Predictions still work without Redis (computed fresh, just uncached). If you train
without Redis you'll get a `503`; with Redis but no worker the job stays `PENDING`.

---

## Key API endpoints

Base URL: `http://localhost:8000/api/v1`

| Method | Path | Notes |
|---|---|---|
| POST | `/register` | `{ email, password }` |
| POST | `/token/` | login → `{ access, refresh }` |
| POST | `/token/refresh/` | `{ refresh }` → `{ access }` |
| GET  | `/stocks/search/?q=` | ranked + fuzzy stock search |
| GET / POST | `/watchlist/` | list / add (`{ stock_id }`) |
| DELETE | `/watchlist/<stock_id>/` | remove |
| GET | `/stocks/<ticker>/` | price history (e.g. `RELIANCE.NS`) |
| GET | `/ml/predict/<ticker>/?days=30` | forecast (404 if untrained) |
| POST | `/ml/train/<ticker>/` | queue async training → `202` + `task_id` |
| GET | `/ml/train/status/<task_id>/` | poll a training job |

---

Based on the project structure from
https://github.com/dev-rathankumar/stock-prediction-portal
