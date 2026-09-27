# SkillSense AI — Backend

FastAPI backend for SkillSense AI. Implements auth, role-based skill
assessments, a rule-based AI evaluation engine, progress tracking, and
PDF/Excel/JSON report generation — matching the data shapes the React
frontend already expects.

## Setup

```bash
cd skillsense-backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then edit SECRET_KEY at least

uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs (Swagger UI) are
at `http://localhost:8000/docs`.

A `skillsense.db` SQLite file is created automatically on first run, and
the 4 roles + 18-question bank are seeded automatically — nothing to load
by hand.

## How it works

- **Auth**: JWT bearer tokens. `bcrypt` password hashing via `passlib`.
- **Roles**: Java Developer, Python Developer, AI Developer, Frontend
  Developer — each with its own topic list and readiness threshold.
- **Assessment**: questions are filtered by the topics relevant to the
  selected role. Submitting answers runs them through `app/ai_engine.py`.
- **AI evaluation engine** (`app/ai_engine.py`): rule-based and fully
  offline — no external API calls, no API key required. It scores each
  topic, flags strengths (≥75%) and gaps (<60%, with a specific mistake
  pattern pulled from the wrong answers), computes a readiness label
  against the role's threshold, and generates a recommendation and a
  30/60/90-day roadmap. `evaluate()` is the one function you'd swap out
  if you later want to call a real LLM instead.
- **Progress**: compares topic scores across a user's last two
  assessments for a role.
- **Reports**: `reportlab` builds the PDF, `openpyxl` builds the Excel
  skill matrix, both generated on demand from the latest assessment.

## API reference

All routes except `/auth/signup` and `/auth/login` require
`Authorization: Bearer <token>`.

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/signup` | Create an account, returns a token |
| POST | `/auth/login` | Log in, returns a token |
| GET | `/auth/me` | Current user |
| PATCH | `/auth/me/role` | Set the user's target role |
| GET | `/roles` | List the 4 target roles |
| GET | `/assessment/questions?role_key=java` | Questions for a role |
| POST | `/assessment/submit` | Submit answers → full AI evaluation |
| GET | `/assessment/latest?role_key=java` | Most recent result for a role |
| GET | `/progress?role_key=java` | Previous vs. current topic scores |
| GET | `/report/json?role_key=java` | Latest result as JSON |
| GET | `/report/pdf?role_key=java` | Downloadable PDF report |
| GET | `/report/excel?role_key=java` | Downloadable Excel skill matrix |

## Try it with curl

```bash
# Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Hasmitha","email":"test@example.com","password":"password123"}'
# → copy the access_token from the response

TOKEN="paste-the-token-here"

# See the roles
curl http://localhost:8000/roles

# Get Java Developer questions
curl "http://localhost:8000/assessment/questions?role_key=java"

# Submit answers (question ids come from the previous call)
curl -X POST http://localhost:8000/assessment/submit \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"role_key":"java","answers":{"1":1,"2":0,"3":2}}'

# Download the PDF report
curl "http://localhost:8000/report/pdf?role_key=java" \
  -H "Authorization: Bearer $TOKEN" -o report.pdf
```

## Connecting the React frontend

The response shapes here mirror `src/data/workflowData.js` in the
frontend almost field-for-field (`skills`, `strengths`, `gaps`,
`readiness`, `recommendation`, `roadmap`, progress points). To wire them
together:

1. Set the frontend's Vite dev server origin in `.env` as
   `CORS_ORIGINS=http://localhost:5173` (already the default).
2. Replace the mock imports in the workflow step components with `fetch`
   calls to these endpoints, storing the JWT (e.g. in memory or
   `localStorage`) after signup/login.
3. The signup/login response shape (`{ access_token, user }`) matches
   what `AuthScreen.jsx` already collects, so the auth screens need the
   least rework.

Happy to do this wiring in a follow-up if you want the two talking to
each other end-to-end.

## Notes

- This is a portfolio/demo build: SQLite, a dev-only default
  `SECRET_KEY`, and permissive CORS. Before deploying anywhere public,
  set a real `SECRET_KEY`, move to PostgreSQL (swap `DATABASE_URL` — the
  SQLAlchemy models don't need to change), and lock down `CORS_ORIGINS`.
- No network access was available while building this, so it hasn't been
  run end-to-end here — double-check `pip install` and the first
  `uvicorn` run on your machine, and let me know if anything errors.
