def api_info(but):
    result = {}
    result['company_fields'] = but.call_list_method('crm.company.fields')
    return result