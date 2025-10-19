from integration_utils.bitrix24.functions import call_list_method, batch_api_call



def api_workers_info(but):
    """ Функция для получения справочной информаци из api """

    result = {}
    #список полей для пользователя
    # result['workers_fields_info'] = but.call_list_method('user.fields')
    # список только активных сотрудников (ACTIVE: True)
    result['active_workers_list'] = but.call_list_method('user.search',{
        'filter': {'ACTIVE': True}
    })
    # список полей для подразделения
    # result['department_fields'] = but.call_list_method('department.fields')
    # список подразделений
    result['department_list'] = but.call_list_method('department.get')
    return result

def safe_int(x):
    """ Преобразуем любой тип данных в int (если ошибка - то возвращает None)"""

    try:
        return int(x)
    except (TypeError, ValueError):
        return None

def add_child_level(departments_by_id):
    """ Добавляет параметры children и level для всех отделов """

    for dep in departments_by_id.values():
        dep['children'] = []
        dep['level'] = 0

    # Заполняем children
    for dep_id, dep in departments_by_id.items():
        parent_id = safe_int(dep.get('PARENT'))
        if parent_id and parent_id in departments_by_id:
            departments_by_id[parent_id]['children'].append(dep_id)


def assign_levels(departments_by_id, dep_id, level=0):
    """ Рекурсивно назначает уровни вложенности отделов """

    departments_by_id[dep_id]['level'] = level
    for child_id in departments_by_id[dep_id]['children']:
        assign_levels(departments_by_id, child_id, level + 1)


def get_all_children(departments_by_id, dep_id):
    """ Возвращает список всех дочерних отделов """

    result = []
    for child_id in departments_by_id[dep_id]['children']:
        result.append(child_id)
        result.extend(get_all_children(departments_by_id, child_id))
    return result


def get_department_chain_for_user(departments_by_id, user_deps):
    """ Формирует цепочку отделов для пользователя """

    user_deps = [safe_int(d) for d in user_deps if d in departments_by_id]
    if not user_deps:
        return []
    max_level = max(departments_by_id[d]['level'] for d in user_deps)
    result = set()
    for level in range(max_level, -1, -1):
        for dep_id, dep in departments_by_id.items():
            if dep['level'] == level:
                all_children = get_all_children(departments_by_id, dep_id)
                if dep_id in user_deps or any(c in user_deps for c in all_children):
                    result.add(dep_id)
                    parent = dep.get('PARENT')
                    while parent:
                        parent = safe_int(parent)
                        result.add(parent)
                        parent = departments_by_id.get(parent, {}).get('PARENT')
    return sorted(result, key=lambda d: departments_by_id[d]['level'], reverse=True)