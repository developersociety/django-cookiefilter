DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

USE_TZ = True

SECRET_KEY = "cookiefilter"  # noqa:S105

INSTALLED_APPS = ["cookiefilter"]
