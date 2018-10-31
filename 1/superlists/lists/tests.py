from django.urls import resolve
from django.test import TestCase

from lists.views import home_page


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        # for explanation of resolve(), see:
        # https://docs.djangoproject.com/en/2.1/ref/urlresolvers/#resolve
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        # instead of manually creating an HttpRequest object (as we did
        # in the earlier version of this test, we can use self.client.get
        # (part of the Django extensions to TestCase)
        response = self.client.get('/')  # the view returns a HttpResponse
                                         # object

        # We don't need to test constants, we can just test that the right
        # template gets loaded (the functional test will still prove that
        # the right content is shown to the user).
        # We'll leave the constant-checking here for now, to make sure
        # everything is working the way we think it is.
        
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

        self.assertTemplateUsed(response, 'lists/home.html')
