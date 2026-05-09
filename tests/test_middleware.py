import re
import warnings

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from cookiefilter.middleware import CookieFilterMiddleware


# Minimal view with response for testing middleware
def get_response(request):
    return HttpResponse(request)


class TestCookieFilterMiddleware(SimpleTestCase):
    def setUp(self):
        # Ensure lru_cache is cleared before each run
        CookieFilterMiddleware.__dict__["allowed_cookies"].fget.cache_clear()
        CookieFilterMiddleware.__dict__["allowed_patterns"].fget.cache_clear()

    def test_default_allowed_cookies(self):
        middleware = CookieFilterMiddleware(get_response=get_response)

        allowed_cookies = middleware.allowed_cookies
        allowed_patterns = middleware.allowed_patterns

        self.assertSetEqual(
            allowed_cookies, {"csrftoken", "django_language", "sessionid", "messages"}
        )
        self.assertTupleEqual(allowed_patterns, ())

    @override_settings(
        COOKIEFILTER_ALLOWED_NAMES=["analytics", "sessionid"],
        COOKIEFILTER_ALLOWED_PATTERNS=[r"^abtesting-\d+-version$"],
    )
    def test_custom_allowed_cookies(self):
        middleware = CookieFilterMiddleware(get_response=get_response)

        allowed_cookies = middleware.allowed_cookies
        allowed_patterns = middleware.allowed_patterns

        self.assertSetEqual(allowed_cookies, {"analytics", "sessionid"})
        self.assertTupleEqual(allowed_patterns, (re.compile(r"^abtesting-\d+-version$"),))

    @override_settings(COOKIEFILTER_ALLOWED=["legacy"])
    def test_deprecated_allowed_setting(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            middleware = CookieFilterMiddleware(get_response=get_response)

            allowed_cookies = middleware.allowed_cookies

            self.assertSetEqual(allowed_cookies, {"legacy"})
            self.assertTrue(len(w), 1)
            deprecation_warning = w[0]
            self.assertEqual(deprecation_warning.category, DeprecationWarning)
            self.assertEqual(
                deprecation_warning.message.args,
                ("COOKIEFILTER_ALLOWED is deprecated, use COOKIEFILTER_ALLOWED_NAMES instead",),
            )

    def test_standard_cookies(self):
        middleware = CookieFilterMiddleware(get_response=get_response)
        request = RequestFactory().get("/")
        request.COOKIES = {"analytics": "removed", "csrftoken": "token", "sessionid": "secret"}
        request.META = {"HTTP_COOKIE": ""}

        middleware(request=request)

        self.assertEqual(request.COOKIES["csrftoken"], "token")
        self.assertEqual(request.COOKIES["sessionid"], "secret")
        self.assertNotIn("analytics", request.COOKIES)
        self.assertEqual(request.META["HTTP_COOKIE"], "csrftoken=token; sessionid=secret")

    def test_no_changes(self):
        middleware = CookieFilterMiddleware(get_response=get_response)
        request = RequestFactory().get("/")
        request.COOKIES = {"csrftoken": "token"}
        request.META = {"HTTP_COOKIE": "unchanged"}

        middleware(request=request)

        self.assertEqual(request.COOKIES, {"csrftoken": "token"})
        self.assertEqual(request.META["HTTP_COOKIE"], "unchanged")

    def test_all_cookies_removed(self):
        middleware = CookieFilterMiddleware(get_response=get_response)
        request = RequestFactory().get("/")
        request.COOKIES = {"analytics": "removed"}
        request.META = {"HTTP_COOKIE": ""}

        middleware(request=request)

        self.assertEqual(request.COOKIES, {})
        self.assertNotIn("HTTP_COOKIE", request.META)

    @override_settings(
        COOKIEFILTER_ALLOWED_PATTERNS=[r"^abtesting-\d+-version$"],
    )
    def test_regex_cookie_kept(self):
        middleware = CookieFilterMiddleware(get_response=get_response)
        request = RequestFactory().get("/")
        request.COOKIES = {
            "analytics": "removed",
            "csrftoken": "token",
            "abtesting-1-version": "control",
            "abtesting-2-version": "control",
            "abtesting-3-version-fake": "unused",
        }
        request.META = {"HTTP_COOKIE": ""}

        middleware(request=request)

        self.assertIn("csrftoken", request.COOKIES)
        self.assertIn("abtesting-1-version", request.COOKIES)
        self.assertIn("abtesting-2-version", request.COOKIES)
        self.assertNotIn("abtesting-3-version-fake", request.COOKIES)
        self.assertNotIn("analytics", request.COOKIES)
