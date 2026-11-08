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
export DJANGO_DEBUG=1                # local dev only (PowerShell: $env:DJANGO_DEBUG="1"); production refuses to start without secrets
python manage.py seed --admin      # fictional demo club; admin password from SEED_ADMIN_PASSWORD or printed once
python manage.py runserver         # http://localhost:8000/api/docs/
python manage.py test              # must pass before finishing a task; auto-uses web_application.settings_test
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

## Translations
The API localizes its own messages from the `Accept-Language` header (en/de/ar; the frontend forwards its UI language). Wrap user-facing strings in `gettext`/`gettext_lazy` and add them to `locale/<lang>/LC_MESSAGES/django.po`; `.mo` files are built by `python manage.py compilemessages` (needs GNU gettext; the Dockerfile does it). Seeded category/skill names are data, not translated.

## SaaS model (multi-tenant)
- Every `Category`, `Skills`, `Player`, `Plans` row belongs to a `Club`; users join via `Membership` (owner/coach/viewer). Views use `ClubScopedMixin` (`players/access.py`) so a club only ever sees its own data. **Any new club-owned model needs a `club` FK and scoped queries plus a cross-club test.**
- Access: `HasEntitlement` allows an active subscription or an unexpired trial (one trial per club, created at `/api/auth/register/`, never restarted); otherwise HTTP 402. Viewers are read-only; only owners manage team/billing.
- Billing: Stripe Checkout + webhook in `players/billing.py` (inert until `STRIPE_*` env vars are set). Team invites and public plan sharing live in `players/team.py`; seats capped by `MAX_SEATS`.
- Storage: set `GS_BUCKET_NAME` to use Google Cloud Storage for uploads (required on Cloud Run).

## Secrets, environments and tests (rules)
- **No credentials in the repo**: not in code, compose files, workflows or docs. Config comes from env vars; deploy secrets are referenced from the cloud secret manager, CI uses throwaway containers without passwords.
- `settings.py` is safe by default: `DJANGO_DEBUG` off, `DJANGO_SECRET_KEY` and `POSTGRES_HOST` required (SQLite only with `DJANGO_DEBUG=1`).
- **Tests never touch real services.** `manage.py test` switches to `settings_test.py`, which clears all production variables, uses in-memory SQLite (or a local `TEST_POSTGRES_*` database whose name starts with `test`), local media, locmem email and no Stripe. Do not weaken this; new external integrations must be disabled there too.
- Media storage is pluggable (`MEDIA_STORAGE=local|s3|gcs|azure`, `web_application/storage.py`); add providers there, not in views.

## Closed beta switch
`SIGNUPS_OPEN` (default off) gates `/api/auth/register/` (HTTP 403 when closed) so the free trial cannot be started by calling the API directly. The public `POST /api/contact/` form stores `ContactMessage` rows (see Django admin) and e-mails `CONTACT_EMAIL`; it is throttled and has a honeypot field. Keep `NEXT_PUBLIC_SIGNUPS_OPEN` in the frontend build in sync.
