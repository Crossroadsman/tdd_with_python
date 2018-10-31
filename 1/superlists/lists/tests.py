from django.urls import resolve
from django.test import TestCase

from lists.views import home_page


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        # instead of manually creating an HttpRequest object (as we did
        # in the earlier version of this test, we can use self.client.get
        # (part of the Django extensions to TestCase)
        response = self.client.get('/')  # the view returns a HttpResponse
                                         # object

        # We don't need to test constants, we can just test that the right
        # template gets loaded (the functional test will still prove that
        # the right content is shown to the user).
        self.assertTemplateUsed(response, 'lists/home.html')
