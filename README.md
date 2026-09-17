# SwasthyaSarthi AI — Backend

FastAPI backend for Team PowerPuff's SwasthyaSarthi AI (Lenovo LEAP Hackathon 2026).

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Server runs at `http://127.0.0.1:8000` — interactive API docs at `http://127.0.0.1:8000/docs`.

SQLite database file (`swasthyasarthi.db`) is created automatically on first run in the `backend/` folder.

## What's built (core 5)

| Feature | Endpoints |
|---|---|
| Accounts | `POST /auth/signup`, `POST /auth/login`, `GET /auth/me` |
| Habits | `GET /habits/{date}`, `POST /habits`, `GET /habits/what-if/{walk_minutes}?log_date=...` |
| Cycles | `GET /cycles`, `POST /cycles` |
| Chatbot | `POST /chatbot/message` |
| Community | `GET /community/trends` |

All endpoints except `/auth/signup` and `/auth/login` require a Bearer token
(the `token` returned from signup/login) in the `Authorization` header.

## Still to do

1. **Port the full symptom list.** `app/symptom_engine.py` currently has 5 example
   symptoms wired up — copy over the remaining rules from the original JS chatbot
   (all 13+ symptoms, follow-up question logic, quick-reply chip options) following
   the same `SYMPTOM_RULES` dict pattern.
2. **Bonus features** (not yet built — add as new routers following the same
   pattern as `habits_router.py`):
   - Medication interaction checker — static JSON table of known dangerous combos
   - Mental health check-in — daily mood log + simple trend detection (e.g. flag if
     last 3+ entries are below a threshold)
   - Festival/season-aware tips — a static date-range → tip mapping, checked against
     today's date
   - Disease-based govt scheme suggestion — static disease → scheme mapping,
     triggered from the chatbot when a serious condition is detected
3. **Swap SECRET_KEY** in `app/auth.py` — set a real `JWT_SECRET_KEY` environment
   variable before deploying, don't leave the dev default.
4. **CORS origins** in `app/main.py` — add your deployed frontend URL before the
   demo, or `localhost:5173` won't be the only place it needs to work from.

## Notes for your teammate (frontend)

The API contract already shared with them matches these endpoints exactly —
request/response field names use snake_case (`sleep_hours`, not `sleepHours`)
to match Python/Pydantic convention. Flag this if their mock data used camelCase.
