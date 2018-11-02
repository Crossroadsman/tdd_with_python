from django.shortcuts import redirect, render

from .models import Item


def home_page(request):
    if request.method == 'POST':
        Item.objects.create(text=request.POST['item_text'])
        return redirect('/')
    # GET
    items = Item.objects.all()
    template = 'lists/home.html'
    context = {'items': items,}
    return render(request, template, context)
