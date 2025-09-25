from drunc_ui.settings import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
        # avoid database locking issues between Kafka consumer and web app
        # https://docs.djangoproject.com/en/5.1/ref/databases/#database-is-locked-errors
        "OPTIONS": {
            "timeout": 5,
            "transaction_mode": "IMMEDIATE",
        },
    }
}
