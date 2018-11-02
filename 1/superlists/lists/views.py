from django.shortcuts import render

from .models import Item


def home_page(request):
    template = 'lists/home.html'
    if request.method == 'POST':
        item = Item()
        item.text = request.POST['item_text']
        item.save()

        context = {'new_item_text': item.text,}
    else:  # GET
        context = {}
    return render(request, template, context)
