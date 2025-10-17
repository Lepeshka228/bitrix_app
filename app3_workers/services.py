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

def get_department_names(department_hash, user):
    """ Возвращает список отделов для конкретного user """

    return [department_hash.get(dep_id).get('NAME') for dep_id in user.get('UF_DEPARTMENT')]


def chief_forward_list(department_hash, users_hash, user):
    """ Рекурсивная функция для иерархического поиска всех начальников - возвращает список начальников """

    user_id = safe_int(user['ID'])
    chiefs = []
    seen_heads = set()

    user_departments = user.get('UF_DEPARTMENT')
    if not user_departments:
        return []

    dept_depths = [(dep_id, get_department_depth(dep_id, department_hash)) for dep_id in user_departments]
    dept_depths.sort(key=lambda x: x[1], reverse=True)  # отдел с максимальной глубиной первым
    main_dep_id = dept_depths[0][0]

    # отдельно для главного отдела
    add_chiefs_list(main_dep_id, department_hash, user_id, users_hash, seen_heads, chiefs)

    # оставшиеся отделы
    for dep_id in user_departments:
        if dep_id == main_dep_id:
            continue
        add_chiefs_list(dep_id, department_hash, user_id, users_hash, seen_heads, chiefs)

    return chiefs


def safe_int(x):
    """ Преобразуем любой тип данных в int (если ошибка - то возвращает None)"""

    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def get_department_depth(dep_id, department_hash):
    """Рекурсивно вычисляем глубину отдела до корня (самого главного отдела)"""

    dep = department_hash.get(dep_id)
    if not dep:
        return 0
    parent_id = dep.get('PARENT')
    if not parent_id or safe_int(parent_id) not in department_hash:
        return 1
    return 1 + get_department_depth(safe_int(parent_id), department_hash)


def add_chiefs_list(dep_id, department_hash, user_id, users_hash, seen_heads, chiefs):
    """ Изменяет список chiefs """

    current_dep = department_hash.get(dep_id)
    while current_dep:
        head_id = safe_int(current_dep.get('UF_HEAD'))
        parent_id = safe_int(current_dep.get('PARENT'))

        if head_id and head_id != user_id and head_id in users_hash and head_id not in seen_heads:
            head_user = users_hash[head_id]
            chiefs.append(head_user)
            seen_heads.add(head_id)

        if parent_id and parent_id in department_hash:
            current_dep = department_hash[parent_id]
        else:
            current_dep = None
