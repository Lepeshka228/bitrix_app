from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

@main_auth(on_start=True, set_cookie=True)
def index(request):
    ''' Главная страница - перенаправляет на приложения '''

    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())


@main_auth(on_cookies=True)
def reload_index(request):
    ''' Главная страница для возвращения по кнопке "На главную". Загружается по куки '''

    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())