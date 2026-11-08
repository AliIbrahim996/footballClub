"""Django settings for the footballClub API (headless backend).

All deployment-specific values come from environment variables so the same
image runs locally and in Docker Compose.
"""
import os
import secrets
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .storage import build_media_storage, is_local

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


# Safe by default: debug is OFF unless explicitly enabled (DJANGO_DEBUG=1 for local development).
DEBUG = env_bool("DJANGO_DEBUG", False)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Set DJANGO_SECRET_KEY (DJANGO_DEBUG is off).")
    SECRET_KEY = secrets.token_urlsafe(50)  # development only: random per process, so sessions reset on restart

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,backend")
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "http://localhost:3000")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "players",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "web_application.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "web_application.wsgi.application"

# PostgreSQL when POSTGRES_HOST is set (Docker / production). SQLite is only for local development
# (DJANGO_DEBUG=1) or when explicitly allowed; a production process without a database host refuses to start
# instead of silently using throw-away local storage.
if os.environ.get("POSTGRES_HOST"):
    if not os.environ.get("POSTGRES_PASSWORD"):
        raise ImproperlyConfigured("POSTGRES_PASSWORD must be set (and non-empty) when POSTGRES_HOST is set.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "footballclub"),
            "USER": os.environ.get("POSTGRES_USER", "footballclub"),
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "OPTIONS": {"sslmode": os.environ.get("POSTGRES_SSLMODE", "prefer")},  # "require" for Neon/Supabase/Cloud SQL
        }
    }
else:
    if not (DEBUG or env_bool("DJANGO_ALLOW_SQLITE", False)):
        raise ImproperlyConfigured("POSTGRES_HOST is not set. Configure PostgreSQL, or set DJANGO_DEBUG=1 for local SQLite.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("de", "German"), ("ar", "Arabic")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Uploaded images: local disk, or S3 / Google Cloud Storage / Azure Blob chosen by MEDIA_STORAGE (see storage.py).
STORAGES = {
    "default": build_media_storage(os.environ),
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
MEDIA_IS_LOCAL = is_local(STORAGES["default"])

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_RATES": {"login": "30/min", "register": "10/hour", "contact": "5/hour"},
    # Number of trusted reverse proxies in front of Django (the Next.js server counts as one; add your load balancer).
    # DRF then reads the real client IP from X-Forwarded-For instead of throttling everyone as one address.
    "NUM_PROXIES": int(os.environ.get("NUM_PROXIES", "1")),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "footballClub API",
    "DESCRIPTION": "Players, skills evaluation and tactical plans.",
    "VERSION": "2.0.0",
}

# --- Billing / SaaS -------------------------------------------------------------
# Self-service sign-up (and the free trial) is closed until you opt in; the public "contact us" form is the way in meanwhile.
# Keep NEXT_PUBLIC_SIGNUPS_OPEN in the frontend build in sync with this.
SIGNUPS_OPEN = env_bool("SIGNUPS_OPEN", False)
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")  # where "contact us" messages are e-mailed (they are always stored)
TRIAL_DAYS = int(os.environ.get("TRIAL_DAYS", "14"))
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000").rstrip("/")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
MAX_SEATS = int(os.environ.get("MAX_SEATS", "5"))  # coaches + pending invites per club on the paid plan

# Invitation emails. Console backend prints them; set EMAIL_HOST to send real mail.
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend" if os.environ.get("EMAIL_HOST") else "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Pitchside <no-reply@localhost>")