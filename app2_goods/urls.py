from django.urls import path
from . import views

app_name = 'goods'

urlpatterns = [
    path('', views.goods, name='goods'),
    path('/', views.reload_index, name='reload_index')
]
