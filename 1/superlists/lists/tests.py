from django.urls import resolve
from django.test import TestCase
from lists.views import home_page


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        # for explanation of resolve(), see:
        # https://docs.djangoproject.com/en/2.1/ref/urlresolvers/#resolve
        found = resolve('/')
        self.assertEqual(found.func, home_page)
