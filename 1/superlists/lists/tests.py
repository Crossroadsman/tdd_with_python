from django.urls import resolve
from django.test import TestCase

from lists.models import Item
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


class ItemModelTest(TestCase):

    def test_saved_items_can_be_retrieved(self):
        """This test hits the database and thus is not a real unit test.
        It should more properly be described as an integration test.
        We will return to this later.
        """
        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(2, saved_items.count())

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual('The first (ever) list item', first_saved_item.text)
        self.assertEqual('Item the second', second_saved_item.text)
