from django.urls import resolve
from django.http import HttpRequest
from django.test import TestCase

from lists.views import home_page


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        # for explanation of resolve(), see:
        # https://docs.djangoproject.com/en/2.1/ref/urlresolvers/#resolve
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        # the view function returns an HttpResponse object
        response = home_page(request)

        # HttpResponse objects have a .content attribute that
        # contains the 'raw bytes, the ones and zeroes that would be sent
        # down the wire to the user's browser'
        html = response.content.decode('utf8')

        # We determine that the HTML is (at least superficially) valid
        # if it:
        # - starts with the required doctype
        # - contains somewhere the correct title (remember the functional
        #                                         test)
        # - ends with a closing html tag
        self.assertTrue(html.startswith('<!doctype html>'))
        self.assertIn('<title>To-Do lists</title>', html)
        self.assertTrue(html.strip().endswith('</html>'))
