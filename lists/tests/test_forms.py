from django.test import TestCase

from lists.models import Item, List
from lists.forms import ItemForm, ERROR_MESSAGES


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

