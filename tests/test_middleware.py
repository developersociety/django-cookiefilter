from django.http import HttpRequest
from django.test import SimpleTestCase

from cookiefilter.middleware import CookieFilterMiddleware


class TestCookieFilterMiddleware(SimpleTestCase):

    def test_standard_cookies(self):
        middleware = CookieFilterMiddleware()
        request = HttpRequest()
        request.COOKIES = {
            'analytics': 'removed',
            'csrftoken': 'token',
            'sessionid': 'secret',
        }
        request.META = {
            'HTTP_COOKIE': '',
        }

        middleware.process_request(request)

        self.assertEqual(request.COOKIES['csrftoken'], 'token')
        self.assertEqual(request.COOKIES['sessionid'], 'secret')
        self.assertNotIn('analytics', request.COOKIES)
        self.assertEqual(request.META['HTTP_COOKIE'], 'csrftoken=token; sessionid=secret')

    def test_no_changes(self):
        middleware = CookieFilterMiddleware()
        request = HttpRequest()
        request.COOKIES = {
            'csrftoken': 'token',
        }
        request.META = {
            'HTTP_COOKIE': 'unchanged',
        }

        middleware.process_request(request)

        self.assertEqual(request.COOKIES, {'csrftoken': 'token'})
        self.assertEqual(request.META['HTTP_COOKIE'], 'unchanged')

    def test_all_cookies_removed(self):
        middleware = CookieFilterMiddleware()
        request = HttpRequest()
        request.COOKIES = {
            'analytics': 'removed',
        }
        request.META = {
            'HTTP_COOKIE': '',
        }

        middleware.process_request(request)

        self.assertEqual(request.COOKIES, {})
        self.assertNotIn('HTTP_COOKIE', request.META)
