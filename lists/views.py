from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError

from lists.models import Item, List
from lists.forms import ItemForm


def home_page(request):
    template = 'lists/home.html'
    context = {'form': ItemForm()}
    return render(request, template, context)

def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ItemForm()

    if request.method == 'POST':
        form = ItemForm(data=request.POST)
        if form.is_valid():
            form.save(for_list=list_)
            return redirect(list_)

    template = 'lists/list.html'
    context = {'list': list_, 
               'form': form,
    }
    return render(request, template, context)

def new_list(request):
    """Create a new list"""
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List.objects.create()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        template = 'lists/home.html'
        context = {'form': form,}
        return render(request, template, context)

