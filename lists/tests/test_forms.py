import unittest
from unittest.mock import patch
from django.test import TestCase

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm, ERROR_MESSAGES


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
    # interacts with (List and Item) are collaborators, so we mock them
    #
    # the method signature needs to have the mocks injected in the reverse
    # order to which they are patched.
    @patch('lists.forms.List')
    @patch('lists.forms.Item')
    def test_save_creates_new_list_and_item_from_POST_data(
        self, mockItem, mockList
    ):
        # the item instance that the form will have access to is the return
        # value of the mocked Item class (thus we will be able to make
        # assertions on the attributes set on the mock class by the form,
        # e.g., `mock_item.text`). The same applies, mutatis mutandis, for
        # the list instance.
        mock_item = mockItem.return_value
        mock_list = mockList.return_value
        user = Mock()
        form = NewListForm(data={'text': 'new item text'})
        # we need to call `is_valid()` so that the form populates the
        # `.cleaned_data` dictionary where it stores validated data
        form.is_valid()

        # without the following method, this test would only confirm that 
        # we create a value for `text` and `list`. It wouldn't test the 
        # sequence (i.e., that we create these before saving the model 
        # objects and not the other way round).
        # Note that this would be trivial to prove if we weren't using
        # mocks, so we need to be alert to things that would be obvious
        # in a fully-implemented version of our code but aren't
        # certain while we are using test doubles.
        # One approach to address this when using mocks is to create
        # a function to act as a spy and attach it to the mocked object
        # representing the real object's method we want to spy on (in this
        # case `save`)
        def check_item_text_and_list():
            self.assertEqual(mock_item.text, 'new item text')
            self.assertEqual(mock_item.list, mock_list)
            self.assertTrue(mock_list.save.called)
        # note that the sequence of code is significant when using the spy:
        # we need to assign the side effect before calling the function
        # that would trigger the side effect (this might seem too obvious
        # to mention, but it is very easy to overlook)
        mock_item.save.side_effect = check_item_text_and_list

        form.save(owner=user)

        # We've moved the real assertions (that item has text and a list)
        # into the spy. However, the spy will only run (and thus the
        # assertions will only be fired) if the mocked method we attached
        # the spy to actually gets called.
        # Thus we also need the following assert to ensure that the spied
        # method was called:
        self.assertTrue(mock_item.save.called)


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

