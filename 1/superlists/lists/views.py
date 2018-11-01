from django.http import HttpResponse
from django.shortcuts import render


def home_page(request):
    if request.method == 'POST':
        return HttpResponse(request.POST['item_text'])
    # GET
    template = 'lists/home.html'
    return render(request, template)
