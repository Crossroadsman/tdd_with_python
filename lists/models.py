from django.conf import settings
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()


class Item(models.Model):
    text = models.TextField(default='')
    list = models.ForeignKey(
        'List',
        on_delete=models.CASCADE,
        default=None)

    class Meta:
        ordering = ('id',)
        unique_together = ('list', 'text')

    def __str__(self):
        return self.text


class List(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              blank=True,
                              null=True)

    @property
    def name(self):
        first = self.item_set.first()
        if first:
            return self.item_set.first().text
        else:
            return "Empty List"

    @property
    def sharees(self):
        return self.listsharee_set.all()

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])

    @staticmethod
    def create_new(first_item_text, owner=None):
        list_ = List.objects.create(owner=owner)
        Item.objects.create(text=first_item_text, list=list_)
        return list_

    def share(self, email):
        sharee, _ = ListSharee.objects.get_or_create(
            todolist=self,
            email=email
        )
        return sharee

    def __str__(self):
        return f'{self.owner if self.owner else "no owner"}: {self.name}'


class ListSharee(models.Model):
    """ListSharee behaves a bit like a MTM intermediary model.
    If every email was going to be an actual User, we could
    have a user ForeignKey field instead of email. Alternatively,
    we could simply create a MTM field on List.

    However, it doesn't seem right that the act of sharing should
    automatically create a user belonging to a person of a definite
    email address. Only the email address owner should be able to create
    a User with that email address.

    Nor do we want to restrict the sharing to only those people who
    already have accounts.

    Thus the intermediary model has to have an emailfield property and
    be able to check if a user exists with the same email.
    """

    todolist = models.ForeignKey('List', on_delete=models.CASCADE)
    email = models.EmailField()
 
    @property
    def user(self):
        return User.objects.filter(email=self.email).first()

    class Meta:
        unique_together = ('todolist', 'email')

    def __str__(self):
        return f'{self.todolist}: {self.email} (user: {True if self.user else False})'
