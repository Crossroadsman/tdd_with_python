from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm


def home_page(request):
    template = 'lists/home.html'
    context = {'form': ItemForm()}
    return render(request, template, context)

def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)

    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
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
        list_ = List()
        list_.owner = request.user
        list_.save()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        template = 'lists/home.html'
        context = {'form': form,}
        return render(request, template, context)


def my_lists(request, email):
    owner = User.objects.get(email=email)
    template = 'lists/my_lists.html'
    context = {'owner': owner}
    return render(request, template, context)
