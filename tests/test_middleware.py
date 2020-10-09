from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from cookiefilter.middleware import CookieFilterMiddleware


# Minimal view with response for testing middleware
def get_response(request):
    return HttpResponse(request)


class TestCookieFilterMiddleware(SimpleTestCase):
    def test_standard_cookies(self):
        middleware = CookieFilterMiddleware(get_response=get_response)
        request = RequestFactory()
        request.COOKIES = {"analytics": "removed", "csrftoken": "token", "sessionid": "secret"}
        request.META = {"HTTP_COOKIE": ""}

        middleware(request=request)

        self.assertEqual(request.COOKIES["csrftoken"], "token")
        self.assertEqual(request.COOKIES["sessionid"], "secret")
        self.assertNotIn("analytics", request.COOKIES)
        self.assertEqual(request.META["HTTP_COOKIE"], "csrftoken=token; sessionid=secret")

    def test_no_changes(self):
        middleware = CookieFilterMiddleware(get_response=get_response)
        request = RequestFactory()
        request.COOKIES = {"csrftoken": "token"}
        request.META = {"HTTP_COOKIE": "unchanged"}

        middleware(request=request)

        self.assertEqual(request.COOKIES, {"csrftoken": "token"})
        self.assertEqual(request.META["HTTP_COOKIE"], "unchanged")

    def test_all_cookies_removed(self):
        middleware = CookieFilterMiddleware(get_response=get_response)
        request = RequestFactory()
        request.COOKIES = {"analytics": "removed"}
        request.META = {"HTTP_COOKIE": ""}

        middleware(request=request)

        self.assertEqual(request.COOKIES, {})
        self.assertNotIn("HTTP_COOKIE", request.META)
