import logging
import re
import warnings
from functools import lru_cache
from http.cookies import SimpleCookie

from django.conf import settings
from django.contrib.messages.storage.cookie import CookieStorage
from django.utils.functional import classproperty

logger = logging.getLogger(__name__)


class CookieFilterMiddleware:
    """
    Middleware which removes all unwanted cookies.

    By default standard Django cookies are allowed. This setting can be changed either in the
    Django project settings, or by extending this class.
    """

    @classproperty
    @lru_cache(maxsize=1)
    def allowed_cookies(cls):
        default_cookies = [
            settings.CSRF_COOKIE_NAME,
            settings.LANGUAGE_COOKIE_NAME,
            settings.SESSION_COOKIE_NAME,
            CookieStorage.cookie_name,
        ]

        if hasattr(settings, "COOKIEFILTER_ALLOWED"):
            warnings.warn(
                "COOKIEFILTER_ALLOWED is deprecated, use COOKIEFILTER_ALLOWED_NAMES instead",
                DeprecationWarning,
                stacklevel=1,
            )
            return frozenset(settings.COOKIEFILTER_ALLOWED)

        return frozenset(getattr(settings, "COOKIEFILTER_ALLOWED_NAMES", default_cookies))

    @classproperty
    @lru_cache(maxsize=1)
    def allowed_patterns(cls):
        return tuple(
            re.compile(pattern)
            for pattern in getattr(settings, "COOKIEFILTER_ALLOWED_PATTERNS", [])
        )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # First step - find out if there are any unwanted cookies being set
        current_cookies = set(request.COOKIES.keys())
        unwanted_cookies = current_cookies.difference(self.allowed_cookies)

        # Then we filter the unwanted list with allowed_patterns, for scenarios where multiple
        # cookies are set
        if unwanted_cookies and self.allowed_patterns:
            unwanted_cookies = {
                key
                for key in unwanted_cookies
                if not any(pattern.fullmatch(key) for pattern in self.allowed_patterns)
            }

        if unwanted_cookies:
            # There are some unwanted cookies, so we create a new COOKIES dict containing only the
            # cookies we want
            wanted_cookies = current_cookies - unwanted_cookies

            logger.debug("Deleted %d cookie(s)", len(unwanted_cookies))

            request.COOKIES = {key: request.COOKIES[key] for key in wanted_cookies}

            # Other code in Django will inspect HTTP_COOKIES, so we need to recreate this as if the
            # browser only sent these cookies in the first place
            cookies = SimpleCookie(input=request.COOKIES)
            cookie_string = cookies.output(header="", sep=";")
            # cookies.output is usually for output headers, so we need to left strip whitespace
            cookie_string = cookie_string.lstrip()

            if cookie_string:
                request.META["HTTP_COOKIE"] = cookie_string
            else:
                # If there aren't any cookies left, then just remove the header
                del request.META["HTTP_COOKIE"]

        # Now let remaining middleware or the view handle the request
        return self.get_response(request)
