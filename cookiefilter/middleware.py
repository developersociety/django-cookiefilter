import logging
from http.cookies import SimpleCookie

from django.conf import settings
from django.contrib.messages.storage.cookie import CookieStorage

logger = logging.getLogger(__name__)


class CookieFilterMiddleware:
    """
    Middleware which removes all unwanted cookies.

    By default standard Django cookies are allowed. This setting can be changed either in the
    Django project settings, or by extending this class.
    """

    allowed_cookies = frozenset(
        getattr(
            settings,
            "COOKIEFILTER_ALLOWED",
            [
                settings.CSRF_COOKIE_NAME,
                settings.LANGUAGE_COOKIE_NAME,
                settings.SESSION_COOKIE_NAME,
                CookieStorage.cookie_name,
            ],
        )
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # First step - find out if there are any unwanted cookies being set
        current_cookies = set(request.COOKIES.keys())
        unwanted_cookies = current_cookies.difference(self.allowed_cookies)

        if unwanted_cookies:
            # There are some unwanted cookies, so we create a new COOKIES dict containing only the
            # cookies we want
            wanted_cookies = current_cookies.intersection(self.allowed_cookies)

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
