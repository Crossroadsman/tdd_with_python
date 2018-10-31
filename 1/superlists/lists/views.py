from django.shortcuts import render


def home_page(request):
    template = 'lists/home.html'
    return render(request, template)
