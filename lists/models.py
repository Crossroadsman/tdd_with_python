from django.db import models
from django.urls import reverse
from django.conf import settings


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
    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])
