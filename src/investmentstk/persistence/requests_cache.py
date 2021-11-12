import json
import os
from contextlib import contextmanager
from datetime import timedelta, datetime
from pathlib import Path

import requests_cache
from requests_cache import json_serializer

current_folder = Path(__file__).resolve().parent
http_cache_folder = current_folder / "../../.." / "cache" / "http_cache"


def cache_default_options(hours: float = 24):
    """
    Default cache options for a filesystem backend.
    https://requests-cache.readthedocs.io/en/v0.7.4/modules/requests_cache.backends.html#module-requests_cache.backends.filesystem
    """

    return dict(
        backend="filesystem",
        expire_after=timedelta(hours=hours),
        cache_name=http_cache_folder,
        serializer=json_serializer,
    )


@contextmanager
def requests_cache_configured(*, hours: float = 24, **kwargs):
    """
    Wrapper around a configured requests_cache context manager
    """
    args = {**cache_default_options(hours=hours), **kwargs}

    with requests_cache.enabled(**args):
        yield


def delete_cached_requests() -> list[str]:
    deleted_and_valid = []

    for file_path in http_cache_folder.glob("*.json"):
        cache = json.loads(Path(file_path).read_text())
        os.remove(file_path)

        expires = datetime.fromisoformat(cache['expires'])

        if expires <= datetime.utcnow():
            print(f"Skipping expired: {file_path}")
            continue

        deleted_and_valid.append(cache['url'])

    return deleted_and_valid
