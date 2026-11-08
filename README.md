# footballClub â€” API

Django REST API for managing players, skill evaluations and tactical plans.
The web UI is in the **footballClub-frontend** repo (Next.js); run both together with
Docker Compose from there.

## Run locally
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed --admin   # demo data, admin / admin12345
python manage.py runserver
```
Interactive API docs: http://localhost:8000/api/docs/ Â· Admin: http://localhost:8000/admin/

## Main endpoints (`Authorization: Token <key>`)
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/login/` | get token |
| GET | `/api/dashboard/` | totals, top players, category averages |
| CRUD | `/api/players/` | search `?search=`, order `?ordering=` |
| POST | `/api/players/{id}/evaluate/` | `{"ratings":[{"skill":1,"value":4}]}` |
| CRUD | `/api/skills/`, `/api/categories/` | |
| CRUD | `/api/plans/` | tactical plans: PNG `image` + `board` JSON |

## Docker
`docker build -t footballclub-api .` â€” or use the compose file in the frontend repo.
Env: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `POSTGRES_HOST/DB/USER/PASSWORD`, `MEDIA_ROOT`, `SEED_DEMO_DATA`.

## What changed in v2
Server-rendered templates and the embedded iframe were removed; Django is now API-only,
packages were upgraded to current releases (Django 6.1, DRF 3.18), and the tactics board is
rebuilt natively in the frontend.

## Docker Compose (API + PostgreSQL)
```bash
docker compose up --build
```
Copy `.env.example` to `.env` and set real secrets for anything beyond local dev. Demo data (admin / admin12345) is seeded when `SEED_DEMO_DATA=1` - disable it in production.

