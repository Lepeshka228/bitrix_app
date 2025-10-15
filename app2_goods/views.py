from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth


# Create your views here.
@main_auth(on_cookies=True)
def goods(request):
    '''
    Страниуа с формой для генерации qr-кода - Выбор товара и генерация соответствующей
    ссылки на внешнюю страницу
    '''

    res = "Ваши товары здесь. Скоро вы их выберите и перейдёте по qr-коду на внешнюю страницу с этим товаром"
    return render(request, 'app2_goods/goods.html', locals())



@main_auth(on_cookies=True)
def reload_index(request):
    ''' Главная страница для возвращения по кнопке "На главную". Загружается по куки '''

    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())