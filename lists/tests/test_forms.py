import unittest
from unittest.mock import patch, Mock
from django.test import TestCase

from lists.models import Item, List
from lists.forms import (
    ERROR_MESSAGES,
    ItemForm, NewListForm, ExistingListItemForm
)


class ItemFormTest(TestCase):

    def test_form_renders_item_text_input(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_fails_validation_if_blank_items(self):
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [ERROR_MESSAGES['blank item']])

    def test_form_save_handles_saving_to_a_list(self):
        """Ensure that the form's own save() method is being used to
        handle the save mechanics"""
        list_ = List.objects.create()
        form = ItemForm(data={'text': 'some example text'})
        new_item = form.save(for_list=list_)

        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'some example text')
        self.assertEqual(new_item.list, list_)


# like in test_views we are demonstrating isolation by only using the
# basic unittest.TestCase instead of Django's TestCase
class NewListFormTest(unittest.TestCase):

    # Using our collaboration approach, the models that the form
    # interacts with (List and Item) are collaborators, so we could mock
    # them. However, because we are moving the actual heavy lifting into
    # a single helper method on List, we can just mock that one method:
    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_from_POST_if_user_not_authenticated(
        self, mock_List_create_new
    ):
        user = Mock(is_authenticated=False)
        form = NewListForm(data={'text': 'new item text'})
        # we need to call `is_valid()` so that the form populates the
        # `.cleaned_data` dictionary where it stores validated data
        form.is_valid()

        form.save(owner=user)

        # (assert_called_once and assert_called_once_with are assertion
        # methods provided with Mock:
        # https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called_with
        # )
        mock_List_create_new.assert_called_once_with(
            first_item_text='new item text'
        )

    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_and_owner_from_POST_if_user_authenticated(
        self, mock_List_create_new
    ):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()

        form.save(owner=user)

        mock_List_create_new.assert_called_once_with(
            first_item_text='new item text',
            owner=user
        )

    @patch('lists.forms.List.create_new')
    def test_save_returns_new_list_object(self, mock_List_create_new):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()

        response = form.save(owner=user)

        self.assertEqual(response, mock_List_create_new.return_value)


class ExistingListItemFormTest(TestCase):

    def test_renders_placeholder_text(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)

        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_validation_for_blank_items(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': ''})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [ERROR_MESSAGES['blank item']])

    def test_validation_for_duplicate_items(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='foo')
        form = ExistingListItemForm(for_list=list_, data={'text': 'foo'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], 
                         [ERROR_MESSAGES['duplicate item']])

    def test_save(self):
        """Shouldn't need any args passed to save() on this subclass"""
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': 'foo'})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.all()[0])

