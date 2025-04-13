# Django Cookie Filter

[Django](https://www.djangoproject.com/) middleware which removes all unwanted cookies - useful
for improving cache hit ratios when analytics cookies interfere with caching.

## Installation

Using [pip](https://pip.pypa.io/):

```console
$ pip install django-cookiefilter
```

Edit your Django project's settings module, and add the middleware to the start of ``MIDDLEWARE``:

```python
MIDDLEWARE = [
    "cookiefilter.middleware.CookieFilterMiddleware",
    # ...
]
```

> [!NOTE]
> The middleware should be added before ``UpdateCacheMiddleware``, as it uses the value of
> HTTP_COOKIES which needs to be modified.

## Configuration

Out of the box the standard Django cookie names will work without any other configuration. However
if your project uses different or additional cookie names, edit ``COOKIEFILTER_ALLOWED`` in your
project's settings module:

```python
COOKIEFILTER_ALLOWED = [
    "analytics",
    "csrftoken",
    "django_language",
    "messages",
    "sessionid",
]
```
