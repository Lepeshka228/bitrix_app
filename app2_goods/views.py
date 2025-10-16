from appier.legacy import items
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.models import BitrixUser
from django.core.signing import Signer, BadSignature

from .forms import GoodForm
from .services import api_goods_info, generate_qr_code


signer = Signer()
# Create your views here.
@main_auth(on_cookies=True)
def goods(request):
    """
    Страниуа с формой для генерации qr-кода - Выбор товара и генерация соответствующей
    ссылки на внешнюю страницу
    """

    form = GoodForm()

    but = request.bitrix_user_token
    result = api_goods_info(but)
    goods_list_info = result.get('goods_list')    # информация по каждому товару

    if request.method == 'POST':
        form = GoodForm(request.POST)
        if form.is_valid():
            good_id = form.cleaned_data['good_id']
            # подписываю ID
            signed_id = signer.sign(good_id)
            # по ней делаю ссылку
            public_url = request.build_absolute_uri(f"/goods/public/{signed_id}/")
            # генерирую qr
            qr_data = generate_qr_code(public_url)

            return render(request, 'app2_goods/goods_qr.html', {
                'qr_data': qr_data,
                'public_url': public_url,
                'good_id': good_id
            })

    return render(request, 'app2_goods/goods.html', {
        'form': form,
        'goods_list_info': goods_list_info
    })


@main_auth(on_cookies=True)
def goods_autocomplete(request):
    """ Возвращает json списка совпадений по подстроке q """

    query = request.GET.get('q', '').lower()
    but = request.bitrix_user_token
    result = api_goods_info(but)
    goods_list_info = result.get('goods_list')

    # ищу совпадения
    matches = [
        {'ID': g.get('ID'), 'NAME': g.get('NAME')}
        for g in goods_list_info
        if query in g.get('NAME', '').lower()
    ]

    return JsonResponse(matches, safe=False)


def goods_public(request, signed_id):
    """ Публичная страница товара по секретной ссылке """

    try:
        good_id = signer.unsign(signed_id)
    except BadSignature:
        return HttpResponseNotFound("Неверная ссылка")

    # получаю данные о товаре через BitrixUser
    btx_user = BitrixUser.objects.first()   # первого юзера из БД с доступом к приложению (api) вне iframe
    if not btx_user:
        return HttpResponseNotFound("Нет Bitrix-пользователя для запроса данных")

    # достаю токен
    but = btx_user.bitrix_user_token
    if not but:
        return HttpResponseNotFound("Нет токена Bitrix для этого пользователя")

    # запрашиваю товар
    good = but.call_api_method('crm.product.get', {'id': good_id})['result']
    # good_img = but.call_api_method('catalog.productImage.get', {'productId': good_id})
    good_img_info = but.call_api_method('catalog.productImage.list', {'productId': good_id, 'select': ['detailUrl']})\
                                    ['result']['productImages']
    good_img = None
    if good_img_info:
        good_img = good_img_info[0].get('detailUrl')

    if not good:
        return HttpResponseNotFound("Товар не найден в Bitrix")

    return render(request, 'app2_goods/goods_public.html', {'good': good,
                                                            'good_img': good_img})



@main_auth(on_cookies=True)
def reload_index(request):
    ''' Главная страница для возвращения по кнопке "На главную". Загружается по куки '''

    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())