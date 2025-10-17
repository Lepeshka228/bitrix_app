from integration_utils.bitrix24.functions.call_list_method import call_list_method


def api_workers_info(but):
    """ Функция для получения справочной информаци из api """

    result = {}
    #список полей для пользователя
    result['workers_fields_info'] = but.call_list_method('user.fields')
    # список только активных сотрудников (ACTIVE: True)
    result['active_workers_list'] = but.call_list_method('user.search',{
        'filter': {'ACTIVE': True}
    })
    # список полей для подразделения
    result['department_fields'] = but.call_list_method('department.fields')
    # список подразделений
    result['department_list'] = but.call_list_method('department.get')
    return result

def get_department_names(department_hash, user):
    """ Возвращает список отделов для конкретного user """

    return [department_hash.get(dep_id).get('NAME') for dep_id in user.get('UF_DEPARTMENT')]


def chief_froward_list(department_hash, users_hash, user, cache=None):
    """ Рекурсивная функция для иерархического поиска всех начальников - возвращает список начальников """

    if cache is None:
        cache = {}

    user_id = int(user['ID'])
    seen_heads = set()
    chiefs = []

    for dep_id in user.get('UF_DEPARTMENT', []):
        # если уже вычисляли начальников для этого отдела — используем кэш
        if dep_id in cache:
            for c in cache[dep_id]:
                if c['ID'] not in seen_heads:
                    seen_heads.add(c['ID'])
                    chiefs.append(c)
            continue

        # текущий отдел
        current_dep = department_hash.get(dep_id)
        dep_chiefs = []

        while current_dep:
            # id главы отдела и вышестоящего отдела
            head_id = current_dep.get('UF_HEAD')
            parent_id = current_dep.get('PARENT')

            # преобразуем к int - если проблемы, знач None
            try:
                head_id = int(head_id) if head_id else None
                parent_id = int(parent_id) if parent_id else None
            except ValueError:
                head_id = parent_id = None

            # если имеем главу и он не является текущим работником и находится в списке работников
            if head_id and head_id != user_id and head_id in users_hash:
                head_user = users_hash[head_id]
                # добавляем к просмотренным и запоминаем в списках шефов
                if head_id not in seen_heads:
                    seen_heads.add(head_id)
                    dep_chiefs.append(head_user)
                    chiefs.append(head_user)

            # если имеем вышестоящий отдел и он существует в списке отделов
            if parent_id and parent_id in department_hash:
                current_dep = department_hash[parent_id]
            else:
                current_dep = None

        cache[dep_id] = dep_chiefs

    return chiefs
