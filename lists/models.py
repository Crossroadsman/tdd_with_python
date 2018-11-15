from django.db import models
from django.urls import reverse


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

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])
