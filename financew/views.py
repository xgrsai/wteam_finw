from django.shortcuts import render

# Create your views here.
def index(request):
    """головна сторінка фінансиW"""
    return render(request, "financew/index.html")