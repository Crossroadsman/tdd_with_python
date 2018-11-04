from django.shortcuts import redirect, render

from .models import Item


def home_page(request):
    template = 'lists/home.html'
    context = {}
    return render(request, template, context)

def view_list(request):
    items = Item.objects.all()
    template = 'lists/list.html'
    context = {'items': items,}
    return render(request, template, context)

def new_list(request):
    """Create a new list"""
    Item.objects.create(text=request.POST['item_text'])
    return redirect('/lists/the-only-list-in-the-world/')
