from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contacts, name='contacts'),
    path('export_contacts/', views.export_contacts, name='export_contacts')
]
