from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def index(request):
    context = {
        'title': 'Главная'
    }
    return render(request, 'main/index.html', context)
