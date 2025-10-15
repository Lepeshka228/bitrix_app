from django.urls import path
from . import views

app_name = 'goods'

urlpatterns = [
    path('', views.goods, name='goods'),
    path('autocomplete/', views.goods_autocomplete, name='goods_autocomplete'),
    path('public/<str:signed_id>/', views.goods_public, name='goods_public'),

    path('/', views.reload_index, name='reload_index')
]
