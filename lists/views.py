from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError

from .models import Item, List


def home_page(request):
    template = 'lists/home.html'
    context = {}
    return render(request, template, context)

def view_list(request, list_id):
    error = None
    list_ = List.objects.get(id=list_id)

    if request.method == 'POST':
        item = Item(text=request.POST['item_text'], list=list_)
        try:
            item.full_clean()
        except ValidationError:
            error = "You can't have an empty list item"
        else:
            item.save()
            return redirect(f'/lists/{list_.id}/')

    template = 'lists/list.html'
    context = {'list': list_, 'error': error}
    return render(request, template, context)

def new_list(request):
    """Create a new list"""
    list_ = List.objects.create()
    item = Item.objects.create(text=request.POST['item_text'], list=list_)
    try:
        item.full_clean()
    except ValidationError:
        list_.delete()
        context = {'error': "You can't have an empty list item"}
        return render(request, 'lists/home.html', context)
    return redirect(f'/lists/{list_.id}/')

