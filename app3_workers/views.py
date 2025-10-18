from collections import defaultdict, deque

from django.http import HttpResponse

from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from .services import api_workers_info, safe_int


# Create your views here.
@main_auth(on_cookies=True)
def workers(request):
    bitrix_token = request.bitrix_user_token
    api_info = api_workers_info(bitrix_token)

    active_workers_list = api_info['active_workers_list']
    users_by_id = {safe_int(u['ID']): u for u in active_workers_list}

    department_list = api_info['department_list']
    departments_by_id = {safe_int(d['ID']): d for d in department_list}

    # добавляем children и level для каждого отдела
    for dep in departments_by_id.values():
        dep['children'] = []
        dep['level'] = 0

    # заполняем children
    for dep_id, dep in departments_by_id.items():
        parent_id = safe_int(dep.get('PARENT'))
        if parent_id and parent_id in departments_by_id:
            # Добавляем как int, не строку!
            departments_by_id[parent_id]['children'].append(dep_id)

    # рекурсивная функция для уровней
    def assign_levels(dep_id, level=0):
        departments_by_id[dep_id]['level'] = level
        for child_id in departments_by_id[dep_id]['children']:
            assign_levels(child_id, level + 1)

    # стартуем с корней (у кого нет PARENT)
    roots = [dep_id for dep_id, dep in departments_by_id.items() if not dep.get('PARENT')]
    for root in roots:
        assign_levels(root)

    # --- вспомогательные функции ---
    def get_all_children(dep_id):
        result = []
        for child_id in departments_by_id[dep_id]['children']:
            result.append(child_id)
            result.extend(get_all_children(child_id))
        return result

    def get_department_chain_for_user(user_deps):
        user_deps = [safe_int(d) for d in user_deps if d in departments_by_id]
        if not user_deps:
            return []
        max_level = max(departments_by_id[d]['level'] for d in user_deps)
        result = set()
        for level in range(max_level, -1, -1):
            for dep_id, dep in departments_by_id.items():
                if dep['level'] == level:
                    all_children = get_all_children(dep_id)
                    if dep_id in user_deps or any(c in user_deps for c in all_children):
                        result.add(dep_id)
                        parent = dep.get('PARENT')
                        while parent:
                            parent = safe_int(parent)
                            result.add(parent)
                            parent = departments_by_id.get(parent, {}).get('PARENT')
        return sorted(result, key=lambda d: departments_by_id[d]['level'], reverse=True)

    # --- основная логика ---
    result = {}

    for user_id, user in users_by_id.items():
        user_deps = [safe_int(dep_id) for dep_id in user.get('UF_DEPARTMENT', []) if dep_id]
        dep_chain = get_department_chain_for_user(user_deps)
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
