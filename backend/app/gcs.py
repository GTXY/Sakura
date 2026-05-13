"""Google Cloud Storage utilities using Workload Identity (no key file needed)."""

import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

_credentials = None
_storage_client = None


def _get_credentials():
    """Return refreshed GCP credentials from the VM's attached service account."""
    global _credentials
    import google.auth
    import google.auth.transport.requests

    if _credentials is None:
        _credentials, _ = google.auth.default()

    request = google.auth.transport.requests.Request()
    if not _credentials.valid:
        _credentials.refresh(request)
    return _credentials


def _get_client():
    global _storage_client
    if _storage_client is None:
        from google.cloud import storage
        _storage_client = storage.Client()
    return _storage_client


def upload_file(bucket_name: str, object_name: str, data: bytes, content_type: str) -> str:
    """Upload bytes to GCS. Returns the object_name (GCS path)."""
    client = _get_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_string(data, content_type=content_type)
    return object_name


def delete_file(bucket_name: str, object_name: str) -> None:
    """Delete an object from GCS. Silently ignores errors."""
    try:
        client = _get_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        blob.delete()
    except Exception as exc:
        logger.warning("GCS delete failed for %s: %s", object_name, exc)


def signed_url(bucket_name: str, object_name: str, days: int = 7) -> str:
    """Generate a V4 signed URL valid for `days` days."""
    creds = _get_credentials()
    client = _get_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    return blob.generate_signed_url(
        expiration=timedelta(days=days),
        method="GET",
        version="v4",
        service_account_email=creds.service_account_email,
        access_token=creds.token,
    )


def object_to_url(bucket_name: str, object_name: str) -> str:
    """
    Convert a GCS object path to a signed URL.
    If the value already looks like an http URL (legacy local-disk URLs),
    return it as-is so existing records don't break.
    """
    if not object_name:
        return object_name
    if object_name.startswith("http"):
        return object_name
    return signed_url(bucket_name, object_name)
