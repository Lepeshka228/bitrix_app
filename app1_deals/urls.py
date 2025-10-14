from django.urls import path
from . import views

app_name = 'deals'

urlpatterns = [
    path('', views.deals, name='deals'),
    path('add_deal', views.add_deal, name='add_deal'),
    path('/', views.reload_index, name='reload_index')
]
