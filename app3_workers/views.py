from django.http import HttpResponse


from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from .services import api_workers_info, get_department_names, chief_froward_list


# Create your views here.
@main_auth(on_cookies=True)
def workers(request):
    but = request.bitrix_user_token

    api_info = api_workers_info(but)

    active_workers_list = api_info['active_workers_list']
    # хеш для работников по id
    users_by_id = {int(user['ID']): user for user in active_workers_list}

    department_list = api_info['department_list']
    # хеш для отделов по id
    departments_by_id = {int(dep['ID']): dep for dep in department_list}

    result = {}
    for user in active_workers_list:
        user_id = int(user['ID'])
        department_names = get_department_names(departments_by_id, user)
        chiefs = chief_froward_list(departments_by_id, users_by_id, user)
        chief_names = [f"{c['NAME']} {c['LAST_NAME']}" for c in chiefs]
        result[user_id] = {'NAME': user.get('NAME'),
                           'LAST_NAME': user.get('LAST_NAME'),
                           'DEPARTMENTS': department_names,
                           'CHIEFS': chief_names}

    return render(request, 'app3_workers/workers.html', locals())


@main_auth(on_cookies=True)
def reload_index(request):
    ''' Главная страница для возвращения по кнопке "На главную". Загружается по куки '''

    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())
