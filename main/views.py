from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.models.bitrix_user import BitrixUser

@main_auth(on_start=True, set_cookie=True)
def index(request):
    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())