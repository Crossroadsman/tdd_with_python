from django.shortcuts import redirect, render

from .models import Item, List


def home_page(request):
    template = 'lists/home.html'
    context = {}
    return render(request, template, context)

def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    template = 'lists/list.html'
    context = {'list': list_,}
    return render(request, template, context)

def new_list(request):
    """Create a new list"""
    list_ = List.objects.create()
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect(f'/lists/{list_.id}/')

def add_item(request, list_id):
    """Add an item to an existing list"""
    list_ = List.objects.get(id=list_id)
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect(f'/lists/{list_id}/')
