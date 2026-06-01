# Hack2Hire AI Interview Platform

Hack2Hire is a production-style full-stack voice interview platform. It analyzes resumes and job descriptions, creates adaptive technical interviews, transcribes spoken answers with Whisper, evaluates answers with GPT-4o, and generates hiring readiness reports.

## Run With Docker

1. Add your OpenAI key in `backend/.env.example` or copy it to `backend/.env` and update `docker-compose.yml`.
2. Start the stack:

```bash
docker compose up --build
```

3. Open the app at [http://localhost:3000](http://localhost:3000).
4. The API runs at [http://localhost:8000/api](http://localhost:8000/api), and Django admin runs at [http://localhost:8000/admin](http://localhost:8000/admin).

The backend includes deterministic local scoring and extraction fallback logic when `OPENAI_API_KEY` is empty, so the product flow still works for development. Speech-to-text and text-to-speech require a valid OpenAI key.

## Main User Flow

1. Register or log in.
2. Upload a PDF or text resume.
3. Paste a job description or upload a JD file.
4. Start an interview from the dashboard.
5. Record or type answers in the interview room.
6. Submit answers and receive adaptive follow-up questions.
7. Finish the interview and review the hiring readiness report.
8. View analytics for skill match, communication, time management, difficulty progression, and history.

## API Endpoints

Authentication:

- `POST /api/auth/signup/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

Resume and JD:

- `GET /api/resumes/`
- `POST /api/resumes/`
- `GET /api/job-descriptions/`
- `POST /api/job-descriptions/`

Interview:

- `GET /api/sessions/`
- `POST /api/sessions/`
- `POST /api/sessions/{id}/next_question/`
- `POST /api/sessions/{id}/speak/`
- `POST /api/sessions/{id}/finish/`
- `POST /api/answers/`

Reports and analytics:

- `GET /api/reports/`
- `GET /api/reports/{id}/`
- `GET /api/analytics/summary/`

Realtime:

- `ws://localhost:8000/ws/interviews/{session_id}/`

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
USE_SQLITE=1 DJANGO_DEBUG=1 python manage.py migrate
USE_SQLITE=1 DJANGO_DEBUG=1 python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Tests:

```bash
cd backend && USE_SQLITE=1 python manage.py test
cd frontend && npm test
```

## Data Model

The backend stores users, resumes, job descriptions, interview sessions, questions, answers, scores, and reports as normalized relational models. Flexible AI-derived structures such as extracted skills, projects, skill matrices, difficulty progression, communication signals, and radar chart data are stored in JSON fields.
