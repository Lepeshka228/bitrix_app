from datetime import datetime

from django.shortcuts import redirect


def api_deal_info(but):
    '''
    Возвращает информацию из ответа api о полях сделки(fields_info)
    и вариантах выбора для полей(stage, type, currency) !по порядку
    '''

    # обращаюсь к api для инфы о полях сделки
    fields_info = but.call_list_method("crm.deal.fields")
    # для пользовательского поля установил title на русском
    fields_info['UF_CRM_PRIORITY']['title'] = fields_info['UF_CRM_PRIORITY']['listLabel']
    # print(fields_info['UF_CRM_PRIORITY']['title'])
    # это только для полей с параметром statusType
    stage_choices_info = but.call_list_method('crm.status.entity.items', fields={'entityId': 'DEAL_STAGE'})
    type_choices_info = but.call_list_method('crm.status.entity.items', fields={'entityId': 'DEAL_TYPE'})
    currency_choices_info = but.call_list_method('crm.currency.list')
    priority_choices_info = but.call_list_method('crm.deal.userfield.get', fields={'ID': '233'})['LIST']
    return fields_info, stage_choices_info, type_choices_info, currency_choices_info, priority_choices_info

def renaming_fields_and_choices_info(api_deal_info, but):
    '''
    Возвращает словарь с renaimingом
    field_map = {'ID': 'ID', 'TITLE': 'Название', 'TYPE_ID': 'Тип' ...}
    stage_choices = {'NEW': 'Новая', 'PREPARATION': 'Подготовка документов', ...} и т. п.
    '''

    fields_info, stage_choices_info, type_choices_info, currency_choices_info, priority_choices_info = api_deal_info(but)
    # сопоставляю дефолт имя нормальному в словаре
    field_map = {code: info["title"] for code, info in fields_info.items()}
    stage_choices = {item['STATUS_ID']: item['NAME'] for item in stage_choices_info}
    type_choices = {item['STATUS_ID']: item['NAME'] for item in type_choices_info}
    currency_choices = {item['CURRENCY']: item['FULL_NAME'] for item in currency_choices_info}
    priority_choices = {item['ID']: item['VALUE'] for item in priority_choices_info}

    return field_map, stage_choices, type_choices, currency_choices, priority_choices

def choices_options_for_form(api_deal_info, but):
    ''' Возвращает множества (стрём_имя, норм_имя) для выбора ChoiceField в форме '''

    fields_info, stage_choices_info, type_choices_info, currency_choices_info, priority_choices_info = api_deal_info(but)
    stage_choices = [(item['STATUS_ID'], item['NAME']) for item in stage_choices_info]
    type_choices = [(item['STATUS_ID'], item['NAME']) for item in type_choices_info]
    currency_choices = [(item['CURRENCY'], item['FULL_NAME']) for item in currency_choices_info]
    priority_choices = [(item['ID'], item['VALUE']) for item in priority_choices_info]
    return stage_choices, type_choices, currency_choices, priority_choices

def renaming_choices(res, type_choices, stage_choices, currency_choices, priority_choices):
    '''
    Переименовывает значения полей на основе справочной информации type_choices, stage_choices, currency_choices.
    Приводит дату к др виду
    '''
    for deal in res:
        deal['BEGINDATE'] = datetime.fromisoformat(deal['BEGINDATE']).strftime('%d.%m.%Y')
        deal['CLOSEDATE'] = datetime.fromisoformat(deal['CLOSEDATE']).strftime('%d.%m.%Y')
        deal['TYPE_ID'] = type_choices.get(deal['TYPE_ID'])
        deal['STAGE_ID'] = stage_choices.get(deal['STAGE_ID'])
        deal['CURRENCY_ID'] = currency_choices.get(deal['CURRENCY_ID'])
        deal['UF_CRM_PRIORITY'] = priority_choices.get(deal['UF_CRM_PRIORITY'])

def fill_and_create_deal_form(but, form, choices):
    '''
    Заполняет форму пользовательскими данными и создаёт её через api битрикса
    Перенаправляет на redirect_url
    '''

    # назначаю варианты
    form.fields['STAGE_ID'].choices = choices[0]
    form.fields['TYPE_ID'].choices = choices[1]
    form.fields['CURRENCY_ID'].choices = choices[2]
    form.fields['UF_CRM_PRIORITY'].choices = choices[3]

    if form.is_valid():
        data = form.cleaned_data

        # преобразую даты
        for key in ['BEGINDATE', 'CLOSEDATE']:
            if data.get(key):
                data[key] = data[key].strftime('%Y-%m-%dT%H:%M:%S')

        # создаю сделку
        but.call_api_method("crm.deal.add", {"fields": data})

    # return form
