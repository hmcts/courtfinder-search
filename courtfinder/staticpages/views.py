from django.shortcuts import render

def index(request):
    return render(request, 'staticpages/index.jinja')

def error(request):
    return render(request, 'staticpages/error.jinja')

def notfound(request):
    return render(request, 'staticpages/notfound.jinja')
