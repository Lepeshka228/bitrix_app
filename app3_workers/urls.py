from django.urls import path
from . import views

app_name = 'workers'

urlpatterns = [
    path('', views.workers, name='workers'),

    path('/', views.reload_index, name='reload_index')
]
