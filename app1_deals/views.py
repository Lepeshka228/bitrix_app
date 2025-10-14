from datetime import datetime

from django.db.models.expressions import result
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from .forms import DealForm
from .services import api_deal_info, renaming_fields_and_choices_info, choices_options_for_form, renaming_choices, \
    fill_and_create_deal_form


@main_auth(on_cookies=True)
def deals(request):
    ''' Страница с отображением списка 10 последних активных сделок (в порядке убывания даты начала) '''

    # получаю битрикс_юзер_токен для работы с api
    but = request.bitrix_user_token

    # список полей для отображения
    field_list_for_deal = ['ID', 'TITLE', 'TYPE_ID', 'OPPORTUNITY', 'CURRENCY_ID', 'STAGE_ID', 'BEGINDATE', \
                           'CLOSEDATE', 'UF_CRM_PRIORITY']

    # сопоставляю дефолт имя нормальному в словаре
    field_map, stage_choices, type_choices, currency_choices, priority_choices = renaming_fields_and_choices_info(api_deal_info, but)

    # обращаюсь к api методу и вытаскиваю из него список сделок с полями 'select' и фильтром 'filter'
    res = but.call_api_method("crm.deal.list", {
        'select': field_list_for_deal,
        'filter': {'!=CLOSED': 'Y'},   # рассматриваю только активные сделки
        'order': {'BEGINDATE': 'DESC'}    # сортирую по убыванию даты
    })['result'][:10]

    # преобразовываю названия в человеческий формат (заголовки, дата, тип, валюта, стадия)
    renaming_choices(res, type_choices, stage_choices, currency_choices, priority_choices)
    fields = [field_map.get(f) for f in field_list_for_deal]

    return render(request, 'app1_deals/deals.html', locals())


@main_auth(on_cookies=True)
def add_deal(request):
    ''' Страница с формой для добавления сделки '''

    but = request.bitrix_user_token

    stage_choices, type_choices, currency_choices, priority_choices = choices_options_for_form(api_deal_info, but)
    choices = [stage_choices, type_choices, currency_choices, priority_choices]

    print(choices)

    if request.method == "POST":
        form = DealForm(request.POST)
        fill_and_create_deal_form(but, form, choices)
        return redirect('deals:deals')
    else:
        form = DealForm()

    form.fields['STAGE_ID'].choices = choices[0]
    form.fields['TYPE_ID'].choices = choices[1]
    form.fields['CURRENCY_ID'].choices = choices[2]
    form.fields['UF_CRM_PRIORITY'].choices = choices[3]

    return render(request, 'app1_deals/add_deal.html', {'form': form})


@main_auth(on_cookies=True)
def reload_index(request):
    ''' Главная страница для возвращения по кнопке "На главную". Загружается по куки '''

    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())