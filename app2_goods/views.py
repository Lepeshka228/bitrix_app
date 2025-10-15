from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from django.http import HttpResponse



# Create your views here.
@main_auth(on_cookies=True)
def goods(request):
    return HttpResponse('Your goods are here!')

