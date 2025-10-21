from django.urls import path
from . import views

app_name = 'map'

urlpatterns = [
    path('', views.map, name='map'),
    path('external_map/', views.external_map, name='external_map')
]
