from django.urls import resolve
from django.test import TestCase

from lists.models import Item, List
from lists.views import home_page


class HomePageTest(TestCase):

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

    def test_GET_requests_do_not_save_to_db(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)


class ListAndItemModelTest(TestCase):

    def test_saved_items_can_be_retrieved(self):
        """Ensure saaved items are persisted and can be retrieved.

        This test hits the database and thus is not a real unit test.
        It should more properly be described as an integration test.
        We will return to this later.
        """
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)


class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_displays_only_applicable_list_items(self):
        correct_list = List.objects.create()
        Item.objects.create(text='item 1: puppies', list=correct_list)
        Item.objects.create(text='item 2: pens', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other item 1', list=other_list)
        Item.objects.create(text='other item 2', list=other_list)
 
        response = self.client.get(f'/lists/{correct_list.id}/')
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

        #self.assertIn('item 1: puppies', response_text)
        #self.assertIn('item 2: pens', response_text)

        # django provides `assertContains`. Like assertIn but handles
        # the encoding/decoding between response.content bytes and
        # python strings
        # thus we don't need to manually decode response.content into
        # response_text. We've left the original decoding and the
        # old asserts by way of comparison
        self.assertContains(response, 'item 1: puppies')
        self.assertContains(response, 'item 2: pens')
        self.assertNotContains(response, 'other item 1')
        self.assertNotContains(response, 'other item 2')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        # `response.context` represents the context we're going to pass
        # into the render function (the DJango Test Client puts it on the
        # response object for us, to help with testing)
        self.assertEqual(response.context['list'], correct_list)


class NewListTest(TestCase):

    def setUp(self):
        self.item_text = 'A new list item'
        self.post_data = {'item_text': self.item_text}
        self.post_url = '/lists/new'

    def test_can_save_POST_request(self):
        """Make sure the home page can make POST requests that update
        the database
        """
        self.client.post(self.post_url, data=self.post_data)

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, self.item_text)

    def test_redirects_after_POST_request(self):
        """Make sure the home page redirects after a POST"""

        # self.client.post takes a `data` argument that contains a
        # dictionary of the form data, where the key is the
        # form's `name` attribute and the value is whatever we want
        # to supply as a value to that form input.
        response = self.client.post(self.post_url, data=self.post_data)
        
        # We are following the principle of always redirecting after a POST
        # instead of doing two assertEquals, to check that the response.
        # status_code is 302 and the redirect url is /lists/<list_id>/
        # we can use assertRedirects:
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')


class NewItemTest(TestCase):

    def setUp(self):
        self.other_list = List.objects.create()
        self.correct_list = List.objects.create()
        self.add_item_url = f'/lists/{self.correct_list.id}/add_item'
        self.post_data = {'item_text': 'A new item for an existing list'}

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """Make sure that existing lists can get new items"""
        self.client.post(
            self.add_item_url,
            data=self.post_data
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, self.correct_list)

    def test_redirects_to_list_view(self):
        """Make sure that after POSTing to add_item, we redirect to
        list_view
        """
        response = self.client.post(
            self.add_item_url,
            data=self.post_data
        )

        self.assertRedirects(response, f'/lists/{self.correct_list.id}/')
