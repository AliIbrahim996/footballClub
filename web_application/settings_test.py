"""Settings used by ``manage.py test`` (selected automatically in manage.py).

Tests must never reach a real database, payment provider, mail server or bucket, whatever the shell environment holds.
So this module first removes every production variable from the environment, then loads the normal settings and
overrides the database and external services:

  * default: an in-memory SQLite database
  * TEST_POSTGRES_HOST set (CI): a Postgres server, but only a local/service host, and only a database whose name
    starts with "test" -- Django then creates and drops its own ``test_<name>`` copy on top of that.
"""
import os
import tempfile

_PRODUCTION_VARS = (
    "POSTGRES_", "STRIPE_", "EMAIL_", "MEDIA_STORAGE", "MEDIA_PUBLIC", "MEDIA_ROOT", "AWS_", "GS_", "GOOGLE_APPLICATION",
    "AZURE_", "SIGNUPS_", "CONTACT_", "DJANGO_SECRET_KEY", "DJANGO_ALLOWED_HOSTS", "FRONTEND_URL",
)
for _name in list(os.environ):
    if _name.startswith(_PRODUCTION_VARS):
        del os.environ[_name]
os.environ["DJANGO_DEBUG"] = "1"
os.environ["DJANGO_ALLOW_SQLITE"] = "1"

from .settings import *  # noqa: E402,F401,F403
from django.core.exceptions import ImproperlyConfigured  # noqa: E402

_SAFE_HOSTS = {"localhost", "127.0.0.1", "::1", "postgres", "db"}
_pg_host = os.environ.get("TEST_POSTGRES_HOST", "")
if _pg_host:
    _pg_name = os.environ.get("TEST_POSTGRES_DB", "test_footballclub")
    if _pg_host not in _SAFE_HOSTS:
        raise ImproperlyConfigured(f"Refusing to run tests against host {_pg_host!r}; use a local or service-container database.")
    if not _pg_name.startswith("test"):
        raise ImproperlyConfigured("TEST_POSTGRES_DB must start with 'test'.")
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _pg_name,
            "USER": os.environ.get("TEST_POSTGRES_USER", "footballclub"),
            "PASSWORD": os.environ.get("TEST_POSTGRES_PASSWORD", ""),
            "HOST": _pg_host,
            "PORT": os.environ.get("TEST_POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

SECRET_KEY = "test-only-not-a-secret-" + "x" * 32
STORAGES = {  # noqa: F405
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
MEDIA_ROOT = tempfile.mkdtemp(prefix="pitchside-test-media-")
MEDIA_IS_LOCAL = True
STRIPE_SECRET_KEY = STRIPE_PRICE_ID = STRIPE_WEBHOOK_SECRET = ""
SIGNUPS_OPEN = True
CONTACT_EMAIL = "owner@example.test"
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # fast; never used outside tests
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_RATES": {"login": "1000/min", "register": "1000/min", "contact": "1000/min"}}  # noqa: F405
