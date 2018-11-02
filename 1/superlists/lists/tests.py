from django.urls import resolve
from django.test import TestCase

from lists.models import Item
from lists.views import home_page


class HomePageTest(TestCase):
    def setUp(self):
        self.item_text = 'A new list item'
        self.post_data = {'item_text': self.item_text}

    def test_GET_uses_home_template(self):
        """Make sure that GET requests use the correct template"""
        # instead of manually creating an HttpRequest object (as we did
        # in the earlier version of this test, we can use self.client.get
        # (part of the Django extensions to TestCase)
        response = self.client.get('/')  # the view returns a HttpResponse
                                         # object

        # We don't need to test constants, we can just test that the right
        # template gets loaded (the functional test will still prove that
        # the right content is shown to the user).
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_can_save_POST_request(self):
        """Make sure the home page can make POST requests that update
        the database
        """
        self.client.post('/', data=self.post_data)

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, self.item_text)

    def test_redirects_after_POST_request(self):
        """Make sure the home page redirects after a POST"""

        # self.client.post takes a `data` argument that contains a
        # dictionary of the form data, where the key is the
        # form's `name` attribute and the value is whatever we want
        # to supply as a value to that form input.
        response = self.client.post('/', data=self.post_data)
        
        # We are following the principle of always redirecting after a POST
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/lists/the-only-list-in-the-world/')

    def test_GET_requests_do_not_save_to_db(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)

    def test_displays_all_list_items(self):
        Item.objects.create(text='item 1: puppies')
        Item.objects.create(text='item 2: pens')

        response = self.client.get('/')
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

        self.assertIn('item 1: puppies', response_text)
        self.assertIn('item 2: pens', response_text)


class ItemModelTest(TestCase):

    def test_saved_items_can_be_retrieved(self):
        """Ensure saaved items are persisted and can be retrieved.

        This test hits the database and thus is not a real unit test.
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
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(second_saved_item.text, 'Item the second')


class ListViewTest(TestCase):

    def test_displays_all_items(self):
        Item.objects.create(text='item 1: puppies')
        Item.objects.create(text='item 2: pens')

        response = self.client.get('/lists/the-only-list-in-the-world/')

        # django provides `assertContains`. Like assertIn but handles
        # the encoding/decoding between response.content bytes and
        # python strings
        self.assertContains(response, 'item 1: puppies')
        self.assertContains(response, 'item 2: pens')
