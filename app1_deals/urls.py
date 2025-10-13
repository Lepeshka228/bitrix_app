from django.urls import path
from . import views

app_name = 'deals'

urlpatterns = [
    path('', views.deals, name='deals'),
    path('/', views.reload_index, name='reload_index')
]
