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

    def test_default_allowed_cookies(self):
        middleware = CookieFilterMiddleware(get_response=get_response)

        allowed_cookies = middleware.allowed_cookies

        self.assertSetEqual(
            allowed_cookies, {"csrftoken", "django_language", "sessionid", "messages"}
        )

    @override_settings(COOKIEFILTER_ALLOWED_NAMES=["analytics", "sessionid"])
    def test_custom_allowed_cookies(self):
        middleware = CookieFilterMiddleware(get_response=get_response)

        allowed_cookies = middleware.allowed_cookies

        self.assertSetEqual(allowed_cookies, {"analytics", "sessionid"})

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
