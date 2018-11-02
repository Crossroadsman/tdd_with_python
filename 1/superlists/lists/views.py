from django.shortcuts import render

from .models import Item


def home_page(request):
    template = 'lists/home.html'
    if request.method == 'POST':
        new_item_text = request.POST['item_text']
        Item.objects.create(text=new_item_text)

        context = {'new_item_text': new_item_text,}
    else:  # GET
        context = {}
    return render(request, template, context)
