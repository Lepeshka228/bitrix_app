from appier.legacy import items
from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from .forms import GoodForm
from .services import api_goods_info

# Create your views here.
@main_auth(on_cookies=True)
def goods(request):
    '''
    Страниуа с формой для генерации qr-кода - Выбор товара и генерация соответствующей
    ссылки на внешнюю страницу
    '''

    form = GoodForm()

    but = request.bitrix_user_token
    result = api_goods_info(but)
    # res = "Ваши товары здесь. Скоро вы их выберите и перейдёте по qr-коду на внешнюю страницу с этим товаром"

    goods_fields_info = result.get('goods_fields')
    goods_list_info = result.get('goods_list')
    goods_property_fields = result.get('goods_property_fields')

    goods_list_of_names = []
    for good_info in goods_list_info:
        goods_list_of_names.append(good_info.get('NAME'))

    print(goods_list_of_names)
    print(goods_list_info)
    print('goods_property_fields')
    print(goods_property_fields)

    return render(request, 'app2_goods/goods.html', locals())



@main_auth(on_cookies=True)
def reload_index(request):
    ''' Главная страница для возвращения по кнопке "На главную". Загружается по куки '''

    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())