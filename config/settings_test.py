from .settings import *

ELASTIC_APM = {**ELASTIC_APM, "ENABLED": False}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}
