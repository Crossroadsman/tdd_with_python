from django.urls import resolve
from django.test import TestCase

from lists.views import home_page


class HomePageTest(TestCase):
    def setUp(self):
        self.item_text = 'A new list item'
        self.post_data = {'item_text': self.item_text}

    def test_home_page_GET_uses_home_template(self):
        # instead of manually creating an HttpRequest object (as we did
        # in the earlier version of this test, we can use self.client.get
        # (part of the Django extensions to TestCase)
        response = self.client.get('/')  # the view returns a HttpResponse
                                         # object

        # We don't need to test constants, we can just test that the right
        # template gets loaded (the functional test will still prove that
        # the right content is shown to the user).
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_home_page_POST_uses_home_template(self):
        response = self.client.post('/', data=self.post_data)
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_home_page_can_save_POST_request(self):

        # self.client.post takes a `data` argument that contains a
        # dictionary of the form data, where the key is the
        # form's `name` attribute and the value is whatever we want
        # to supply as a value to that form input.
        response = self.client.post('/', data=self.post_data)

        # The HttpResponse object has a `content` attribute which is of
        # type byte sequence (`bytes`)
        # `bytes` has a `decode(encoding="utf-8", errors="strict)` method
        # note that content is utf-8 encoded so we can use the defaults
        # for `decode`
        response_text = response.content.decode()
        # The following print statements are just to visually compare
        # the byte sequence and the python string
        print("----- Here is what the (utf-8 encoded) byte sequence looks like -----")
        print(response.content)
        print("----- End bytestring -----")
        print("----- Here is what the Python string looks like -----")
        print(response_text)
        print("----- End Python string -----")
        self.assertIn(self.item_text, response_text)
