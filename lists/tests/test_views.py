import unittest
from unittest.mock import patch, Mock

from django.http import HttpRequest
from django.test import TestCase
from django.utils.html import escape
from django.contrib.auth import get_user_model
User = get_user_model()

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm, ERROR_MESSAGES
from lists.views import new_list2


class HomePageTest(TestCase):

    # We can remove specific references to GET requests because this view
    # only handles GET requests.
    def test_uses_home_template(self):
        """Make sure that requests use the correct template"""
        # instead of manually creating an HttpRequest object (as we did
        # in the earlier version of this test, we can use self.client.get
        # (part of the Django extensions to TestCase)
        response = self.client.get('/')  # the view returns a HttpResponse
                                         # object

        # We don't need to test constants, we can just test that the right
        # template gets loaded (the functional test will still prove that
        # the right content is shown to the user).
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_requests_do_not_save_to_db(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)

    def test_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):

    # Helper methods
    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

    # Tests
    def test_GET_renders_list_template(self):
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

    def test_can_save_a_POST_request_to_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_valid_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )
        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_invalid_POST_doesnt_save_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_invalid_POST_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_invalid_POST_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_empty_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(ERROR_MESSAGES['blank item']))

    def test_duplicate_input_shows_error_on_page(self):
        list_ = List.objects.create()
        item1 = Item.objects.create(list=list_, text='foo')
        response = self.client.post(
            f'/lists/{list_.id}/',
            data={'text': 'foo'}
        )

        expected_error = escape(ERROR_MESSAGES['duplicate item'])
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'lists/list.html')
        self.assertEqual(Item.objects.all().count(), 1)

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')


# note the distinction between 'integrated' test and 'integration test'
class NewListViewIntegratedTest(TestCase):

    def setUp(self):
        self.item_text = 'A new list item'
        self.post_data = {'text': self.item_text}
        self.post_url = '/lists/new'

    def test_can_save_POST_request(self):
        """Make sure the home page can make POST requests that update
        the database
        """
        self.client.post(self.post_url, data=self.post_data)

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, self.item_text)

    def test_redirects_to_list_view_after_valid_POST_request(self):
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

    def test_invalid_POST_renders_home_page_template(self):
        self.item_text = ''
        self.post_data = {'text': self.item_text}
        response = self.client.post(self.post_url, self.post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_invalid_POST_shows_errors_on_home_page_templat(self):
        self.item_text = ''
        self.post_data = {'text': self.item_text}
        response = self.client.post(self.post_url, self.post_data)
        expected_error = escape(ERROR_MESSAGES['blank item'])
        self.assertContains(response, expected_error)

    def test_invalid_POST_passes_form_to_template(self):
        self.item_text = ''
        self.post_data = {'text': self.item_text}
        response = self.client.post(self.post_url, self.post_data)
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_invalid_list_items_arent_saved(self):
        self.item_text = ''
        self.post_data = {'text': self.item_text}
        self.client.post(self.post_url, self.post_data)
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    @unittest.skip
    def test_list_is_linked_to_owner_if_user_authenticated(self):
        user = User.objects.create(email='a@b.com')

        # `force_login()` is the Django test system's way of simulating
        # the effect of logging a user into the site. It should be used
        # in place of `login()` when a test requires that a user be logged
        # in but the details of how the user logged in aren't important.
        self.client.force_login(user)
        self.client.post(self.post_url, data=self.post_data)
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


# Note that the Django TestCase class makes it too easy to write integrated
# tests. To help force us to write 'pure' isolated unit tests, we'll use
# only unittest.TestCase.
#
# NewListForm is going to be the key collaborator for our NewList view, so
# we want to mock out that class and we want to do it at the TestCase's
# class-level.
#
# we also mock out `redirect()` since it is also a collaborator in all of
# our tests
@patch('lists.views.redirect')
@patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):

    # Here we're building up a POST request by hand instead of using the 
    # (integrated) Django Test Client
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = Mock()

    # In this test we check that the view initialises its collaborator
    # (NewListForm) with the correct initial data: the data from the request
    def test_POST_passes_data_to_NewListForm(
        self, mockNewListForm, mock_redirect
    ):
        new_list2(self.request)

        mockNewListForm.assert_called_once_with(data=self.request.POST)

    def test_form_saves_with_owner_if_form_valid(
        self, mockNewListForm, mock_redirect
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        new_list2(self.request)

        mock_form.save.assert_called_once_with(owner=self.request.user)

    def test_redirects_to_object_returned_by_form_if_form_valid(
        self, mockNewListForm, mock_redirect
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = new_list2(self.request)
 
        # we check that the response from the view is return value of
        # the `redirect` function.
        self.assertEqual(response, mock_redirect.return_value)
        # and we check that the `redirect` function was called with
        # the object that the form returns on `save()`
        mock_redirect.assert_called_once_with(mock_form.save.return_value)

    @patch('lists.views.render')
    def test_renders_home_template_and_form_if_form_invalid(
        self, mock_render, mockNewListForm, mock_redirect
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        response = new_list2(self.request)

        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'lists/home.html', {'form': mock_form}
        )

    def test_does_not_save_if_form_invalid(
        self, mockNewListForm, mock_redirect
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        new_list2(self.request)

        self.assertFalse(mock_form.save.called)


class MyListsTests(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'lists/my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')

        response = self.client.get('/lists/users/a@b.com/')

        self.assertEqual(response.context['owner'], correct_user)
