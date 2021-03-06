from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
User = get_user_model()

from lists.models import Item, List, ListSharee
from lists.forms import ItemForm, ExistingListItemForm, NewListForm


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


# This will eventually replace `new_list()`
def new_list(request):
    """Create a new list"""
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    template = 'lists/home.html'
    context = {'form': form}
    return render(request, template, context)


def my_lists(request, email):
    owner = User.objects.get(email=email)

    # see https://docs.djangoproject.com/en/2.1/ref/models/querysets/#select-related
    lists_shared_with_owner = set()
    for listsharee in ListSharee.objects.filter(email=email).select_related('todolist'):
        lists_shared_with_owner.add(listsharee.todolist)

    template = 'lists/my_lists.html'
    context = {'owner': owner,
               'shared_lists': lists_shared_with_owner}
    return render(request, template, context)


def share_list(request, list_id):
    list_ = List.objects.get(pk=list_id)
    email = request.POST['sharee']
    list_.share(email)

    sharees = list_.sharees
    return redirect(list_)
