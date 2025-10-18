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
