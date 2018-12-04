from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

from lists.models import Item, List


class ItemModelTest(TestCase):

    def test_default_text(self):
        """This really tests that we have an Item object with at least one
        field
        """
        item = Item()
        self.assertEqual(item.text, '')

    def test_item_is_related_to_list(self):
        test_list = List.objects.create()
        item = Item()
        item.list = test_list
        item.save()

        self.assertIn(item, test_list.item_set.all())

    def test_empty_list_is_invalid(self):
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
            # This is an application-level constraint so a violation is
            # a ValidationError, whereas a constraint violation on save()
            # is a DB-level violation so raises IntegrityError
            item.save()
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        test_list = List.objects.create()
        Item.objects.create(list=test_list, text='foo')
        with self.assertRaises(ValidationError):
            item = Item(list=test_list, text='foo')
            item.full_clean()

    def test_can_save_same_item_to_different_lists(self):
        list1 = List.objects.create()
        list2 = List.objects.create()
        item_text = 'bar'
        Item.objects.create(list=list1, text=item_text)
        item = Item(list=list2, text=item_text)
        item.full_clean()  # should not raise

    def test_queryset_preserves_insertion_order(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='i1')
        item2 = Item.objects.create(list=list1, text='item 2')
        item3 = Item.objects.create(list=list1, text='3')

        self.assertEqual(
            list(Item.objects.all()),
            [item1, item2, item3]
        )

    def test_item_string_representation_is_itemtext(self):
        item = Item(text='some text')
        self.assertEqual(str(item), 'some text')


class ListModelTest(TestCase):

    def test_List_get_absolute_url(self):
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.id}/')

    def test_lists_can_have_owners(self):
        user = User.objects.create(email='a@b.com')
        list_ = List.objects.create(owner=user)
        self.assertIn(list_, user.list_set.all())

    def test_list_owner_is_optional(self):
        List.objects.create()  # should not raise

    def test_list_name_is_first_item_text(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='first item')
        Item.objects.create(list=list_, text='second item')

        self.assertEqual(list_.name, 'first item')

