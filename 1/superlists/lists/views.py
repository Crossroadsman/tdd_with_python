from django.shortcuts import redirect, render

from .models import Item, List


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
    list_ = List.objects.create()
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect('/lists/the-only-list-in-the-world/')
