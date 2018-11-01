from django.http import HttpResponse
from django.shortcuts import render


def home_page(request):
    template = 'lists/home.html'
    if request.method == 'POST':
        context = {'new_item_text': request.POST['item_text']}
    else:  # GET
        context = {}
    return render(request, template, context)
