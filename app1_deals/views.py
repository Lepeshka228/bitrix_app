from datetime import datetime

from django.db.models.expressions import result
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

@main_auth(on_cookies=True)
def deals(request):
    # получаю битрикс_юзер_токен для работы с api
    but = request.bitrix_user_token

    # обращаюсь к api для инфы о полях сделки
    fields_info = but.call_api_method("crm.deal.fields")["result"]

    # обращаюсь к api методу и вытаскиваю из него список сделок с полями 'select' и фильтром 'filter'
    res = but.call_api_method("crm.deal.list", {
        'select': ['ID', 'TITLE', 'TYPE_ID', 'OPPORTUNITY', 'CURRENCY_ID', 'STAGE_ID', 'BEGINDATE', 'CLOSEDATE'],
        'filter': {'!=CLOSED': 'Y'},   # рассматриваю только активные сделки
        'order': {'BEGINDATE': 'DESC'}    # сортирую по убыванию даты
    })['result'][:10]

    # преобразовываю дату в человеческий формат
    for deal in res:
        deal['BEGINDATE'] = datetime.fromisoformat(deal['BEGINDATE']).strftime('%d.%m.%Y %H:%M')
        deal['CLOSEDATE'] = datetime.fromisoformat(deal['CLOSEDATE']).strftime('%d.%m.%Y %H:%M')

    # у каждого поля есть в метаданных значение title с норм названием
    # создаю словарь с сопоставлением исходного названия и адекватного
    title_map = {code: info["title"] for code, info in fields_info.items()}

    deals_renamed = []
    for deal in res:
        new_deal = {title_map.get(k, k): v for k, v in deal.items()}
        deals_renamed.append(new_deal)

    # заголовки - ключи первой сделки
    fields = deals_renamed[0].keys() if deals_renamed else []

    return render(request, 'app1_deals/deals.html', locals())


@main_auth(on_cookies=True)
def reload_index(request):
    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())