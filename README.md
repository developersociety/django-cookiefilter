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
if your project uses different or additional cookie names, edit ``COOKIEFILTER_ALLOWED_NAMES`` in
your project's settings module:

```python
COOKIEFILTER_ALLOWED_NAMES = [
    "analytics",
    "csrftoken",
    "django_language",
    "messages",
    "sessionid",
]
```

> [!NOTE]
> This setting was previously named ``COOKIEFILTER_ALLOWED``, which is now deprecated and will be
> removed in a future version.

Or if you need to allow multiple cookies that don't have specific names, you can add
``COOKIEFILTER_ALLOWED_PATTERNS`` to allow additional cookie names with regular expressions:

```python
COOKIEFILTER_ALLOWED_PATTERNS = [
    r"^abtesting-\d+-version$",
]
```
