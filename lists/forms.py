from django import forms

from lists.models import Item


ERROR_MESSAGES = {
    'blank item': "You can't have an empty list item",
}


class ItemForm(forms.models.ModelForm):

    class Meta:
        model = Item
        fields = ('text',)

        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg',
            }),
        }

        # error messages defined here (or in the form field on a regular
        # form) always take precedence over error messages defined at the
        # model level.
        #
        # error_messages is a dictionary where the keys are fields and
        # the values are dictionaries. The inner dictionary's keys are
        # the error name and the value is the error message.
        #
        # the error names are defined by the Field. So, for example
        # (https://docs.djangoproject.com/en/2.1/ref/forms/fields/#django.forms.CharField)
        # CharField has the `required`, `max_length`, and `min_length`
        # error message keys.
        error_messages = {
            'text': {'required': ERROR_MESSAGES['blank item']},
        }
