# AGENTS.md â€” footballClub backend

Headless Django REST API for a football club management app (players, skill
evaluations, tactical plans). The UI lives in the sibling repo
`footballClub-frontend` (Next.js); this repo serves JSON only.

## Stack
- Python 3.12, Django 6.1, Django REST Framework, drf-spectacular (OpenAPI), django-filter
- Auth: DRF token auth (`Authorization: Token <key>`), login at `POST /api/auth/login/`
- DB: PostgreSQL (`POSTGRES_*` env, see `docker-compose.yml`); SQLite fallback only when `POSTGRES_HOST` is unset. Media in `MEDIA_ROOT`
- Prod server: gunicorn + WhiteNoise, packaged by `Dockerfile`

## Layout
- `web_application/` â€” settings (env-driven), root URLs, wsgi/asgi
- `players/models.py` â€” `Category`, `Skills`, `Player`, `PlayerSkills` (rating 1â€“5), `Plans` (PNG + `board` JSON)
- `players/serializers.py`, `players/views.py`, `players/urls.py` â€” API under `/api/`
- `players/migrations/` â€” never edit applied migrations; add new ones
- `players/management/commands/seed.py` â€” demo data (`python manage.py seed --admin`)

## Commands
```bash
python -m venv .venv && .venv/Scripts/activate   # Windows; use bin/activate elsewhere
pip install -r requirements.txt
python manage.py migrate
python manage.py seed --admin      # demo data + admin/admin12345 (dev only)
python manage.py runserver         # http://localhost:8000/api/docs/
python manage.py test              # must pass before finishing a task
```

## Conventions
- Keep views thin; validation lives in serializers. New endpoints get a test in `players/tests.py`.
- Every endpoint requires auth except `auth/login/` and `health/`.
- Config comes from env vars (see `web_application/settings.py`); never hard-code secrets.
- Use `gettext_lazy` (not the removed `ugettext_lazy`). Pin upgraded dependencies in `requirements.txt`.
- Changing a model => `makemigrations`, run tests, and update the frontend types if the API shape changes.

## Do not
- Commit `db.sqlite3`, uploaded media, or `.env`.
- Re-introduce server-rendered templates; the frontend owns all UI.

## Skills
- `.claude/skills/django-security/SKILL.md` (from affaan-m/ECC): follow it for auth, settings hardening and deployment changes. Before production, apply its checklist (HTTPS, secure cookies, HSTS, `DEBUG=False`).

- `.claude/skills/` also holds `django-*` skills from MohamedMandour10/agentic-django (architecture, ORM, migrations, views/APIs, admin, testing, production ops) and `api-designer` (Jeffallan/claude-skills). Load the matching one before changing that layer. Note: this codebase uses DRF ViewSets for simple CRUD; prefer explicit `APIView` + services/selectors when logic grows beyond CRUD.
