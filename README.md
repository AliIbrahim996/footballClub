# footballClub — API

[![Support on Patreon](https://img.shields.io/badge/Support%20on-Patreon-F96854?logo=patreon&logoColor=white)](https://patreon.com/AliIbrahim870)

Django REST API behind **Pitchside**: multi-tenant clubs, players, skill evaluations, tactical plans, a one-time free trial per club, Stripe billing, team invites and public plan sharing. The web UI is in the **footballClub-frontend** repo (Next.js); run both together with Docker Compose from there.

![Dashboard](docs/screenshots/dashboard.jpg)
![Tactics board](docs/screenshots/tactics.jpg)

> Screenshots show the frontend with fictional demo data.

## Run locally
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed --admin   # demo club + admin / admin12345 (dev only)
python manage.py runserver
```
Interactive API docs: http://localhost:8000/api/docs/ · Admin: http://localhost:8000/admin/

## Main endpoints (`Authorization: Token <key>`)
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register/` | create club (14-day trial) + owner, returns token |
| POST | `/api/auth/login/` · `/api/auth/accept-invite/` | sign in · join a club by invite |
| GET | `/api/auth/me/` | user + club status (trial / active / past_due / canceled) |
| GET | `/api/dashboard/` | totals, top players, category averages |
| CRUD | `/api/players/` | search `?search=`, order `?ordering=` |
| POST | `/api/players/{id}/evaluate/` | `{"ratings":[{"skill":1,"value":4}]}` |
| CRUD | `/api/skills/`, `/api/categories/`, `/api/plans/` | plans: PNG `image` + `board` JSON |
| GET/POST/DELETE | `/api/team/`, `/api/team/invites/`, `/api/team/members/{id}/` | owner-only team management, seat limit |
| POST/DELETE | `/api/plans/{id}/share/` · GET `/api/shared/{token}/` | public read-only plan link |
| POST | `/api/billing/checkout/` · `/portal/` · `/webhook/` | Stripe (inert until configured) |

All club data is scoped to the caller's club. An expired trial/subscription returns **HTTP 402**. Messages follow `Accept-Language` (en/de/ar).

## Docker Compose (API + PostgreSQL)
```bash
docker compose up --build
```
Copy `.env.example` to `.env` and set real secrets for anything beyond local dev. Demo data (admin / admin12345) is seeded when `SEED_DEMO_DATA=1` — disable it in production.
Standalone image: `docker build -t footballclub-api .`. For Google Cloud Run (Cloud Storage uploads, `POSTGRES_SSLMODE`), Stripe and email setup see `docs/DEPLOY.md` in the frontend repo.

## What changed in v2
Server-rendered templates and the embedded iframe were removed; Django is now API-only, packages were upgraded (Django 6.1, DRF 3.18), the app became multi-tenant with billing, and the tactics board is rebuilt natively in the frontend.

## Support the project
If this is useful to you, you can support its development on **[Patreon](https://patreon.com/AliIbrahim870)**.
