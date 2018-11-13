from django.test import TestCase
from django.core.exceptions import ValidationError

from lists.models import Item, List


class ListAndItemModelsTest(TestCase):

    def test_saved_items_can_be_retrieved(self):
        """Ensure saved items are persisted and can be retrieved.

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

    def test_cannot_save_empty_list_items(self):
        test_list = List.objects.create()
        item = Item(list=test_list, text='')
        with self.assertRaises(ValidationError):
            # Django's validation on save behaviour is a little counter-
            # intuitive. Because different DB backends support different
            # levels of constraints, Django wil not try to enforce a 
            # constraint that isn't supported by the DB. In this case
            # SQLite doesn't support a constraint equivalent to
            # `blank=False` (the default for TextField objects)
            # so Django will silently ignore it on save.
            # We can get aroud this by using the manual full validation
            # method `Model.full_clean()`
            item.save()
            item.full_clean()
