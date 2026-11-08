"""Pluggable media storage.

Pick the backend with MEDIA_STORAGE (default ``local``) and the matching settings below. Credentials are never read
from code: on AWS/GCP/Azure use the workload's IAM role / service account / managed identity where possible, otherwise
the provider's standard environment variables (AWS_ACCESS_KEY_ID..., GOOGLE_APPLICATION_CREDENTIALS, AZURE_ACCOUNT_KEY).

    MEDIA_STORAGE=local   files under MEDIA_ROOT (served by Django); fine for one machine / Docker volume
    MEDIA_STORAGE=s3      AWS_STORAGE_BUCKET_NAME [AWS_S3_REGION_NAME] [AWS_S3_ENDPOINT_URL] [AWS_S3_CUSTOM_DOMAIN]
                          (endpoint URL also covers MinIO, Cloudflare R2, DigitalOcean Spaces, Backblaze B2)
    MEDIA_STORAGE=gcs     GS_BUCKET_NAME
    MEDIA_STORAGE=azure   AZURE_ACCOUNT_NAME AZURE_CONTAINER [AZURE_ACCOUNT_KEY | AZURE_CONNECTION_STRING]

MEDIA_PUBLIC=1 (default) expects a publicly readable bucket and returns plain URLs; MEDIA_PUBLIC=0 returns signed,
expiring URLs for private buckets.
"""
from collections.abc import Mapping

from django.core.exceptions import ImproperlyConfigured

_TRUE = {"1", "true", "yes", "on"}
LOCAL_BACKEND = "django.core.files.storage.FileSystemStorage"


def _need(env: Mapping[str, str], name: str, provider: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"MEDIA_STORAGE={provider} requires {name} to be set.")
    return value


def build_media_storage(env: Mapping[str, str]) -> dict:
    """Return a Django STORAGES['default'] entry for the configured provider."""
    provider = env.get("MEDIA_STORAGE", "local").strip().lower() or "local"
    signed = env.get("MEDIA_PUBLIC", "1").strip().lower() not in _TRUE

    if provider == "local":
        return {"BACKEND": LOCAL_BACKEND}

    if provider == "s3":
        options = {"bucket_name": _need(env, "AWS_STORAGE_BUCKET_NAME", "s3"), "default_acl": None, "querystring_auth": signed}
        for var, option in (("AWS_S3_REGION_NAME", "region_name"), ("AWS_S3_ENDPOINT_URL", "endpoint_url"),
                            ("AWS_S3_CUSTOM_DOMAIN", "custom_domain")):
            if env.get(var):
                options[option] = env[var]
        return {"BACKEND": "storages.backends.s3.S3Storage", "OPTIONS": options}

    if provider in {"gcs", "gcp", "google"}:
        return {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
            "OPTIONS": {"bucket_name": _need(env, "GS_BUCKET_NAME", "gcs"), "default_acl": None, "querystring_auth": signed},
        }

    if provider == "azure":
        options = {
            "account_name": _need(env, "AZURE_ACCOUNT_NAME", "azure"),
            "azure_container": _need(env, "AZURE_CONTAINER", "azure"),
            "expiration_secs": 3600 if signed else None,
        }
        if env.get("AZURE_ACCOUNT_KEY"):
            options["account_key"] = env["AZURE_ACCOUNT_KEY"]
        if env.get("AZURE_CONNECTION_STRING"):
            options["connection_string"] = env["AZURE_CONNECTION_STRING"]
        return {"BACKEND": "storages.backends.azure_storage.AzureStorage", "OPTIONS": options}

    raise ImproperlyConfigured(f"Unknown MEDIA_STORAGE {provider!r}; use local, s3, gcs or azure.")


def is_local(storage: Mapping) -> bool:
    return storage.get("BACKEND") == LOCAL_BACKEND
