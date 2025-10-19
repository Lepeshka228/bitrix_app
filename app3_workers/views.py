from collections import defaultdict, deque

from django.http import HttpResponse

from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from .services import api_workers_info, safe_int, add_child_level, assign_levels, get_department_chain_for_user


# Create your views here.
@main_auth(on_cookies=True)
def workers(request):
    bitrix_token = request.bitrix_user_token
    api_info = api_workers_info(bitrix_token)

    active_workers_list = api_info['active_workers_list']
    # хеш по id
    users_by_id = {safe_int(u['ID']): u for u in active_workers_list}

    department_list = api_info['department_list']
    # хеш по id
    departments_by_id = {safe_int(d['ID']): d for d in department_list}

    add_child_level(departments_by_id)
    roots = [dep_id for dep_id, dep in departments_by_id.items() if not dep.get('PARENT')]
    for root in roots:
        assign_levels(departments_by_id, root)

    # --- Формирование результата ---
    result = {}
    for user_id, user in users_by_id.items():
        user_deps = [safe_int(dep_id) for dep_id in user.get('UF_DEPARTMENT', []) if dep_id]
        dep_chain = get_department_chain_for_user(departments_by_id, user_deps)
        dep_names = [departments_by_id[d]['NAME'] for d in dep_chain if d in departments_by_id]

        boss_list = []
        for dep_id in dep_chain:
            dep = departments_by_id.get(dep_id)
            head_id = safe_int(dep.get('UF_HEAD'))
            if head_id and head_id in users_by_id and head_id != user_id:
                boss_list.append(users_by_id[head_id])

        boss_name_list = list(dict.fromkeys(
            [f"{boss['NAME']} {boss['LAST_NAME']}" for boss in boss_list]
        ))

        result[user_id] = {
            'NAME': user.get('NAME'),
            'LAST_NAME': user.get('LAST_NAME'),
            'DEPARTMENTS': dep_names,
            'CHIEFS': boss_name_list
        }

    return render(request, 'app3_workers/workers.html', locals())


@main_auth(on_cookies=True)
def reload_index(request):
    ''' Главная страница для возвращения по кнопке "На главную". Загружается по куки '''

    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())
