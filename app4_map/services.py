def api_info(but):
    result = {}
    # result['company_fields'] = but.call_list_method('crm.company.fields')
    result['company_list'] = but.call_list_method('crm.company.list')
    result['address_list'] = but.call_list_method('crm.address.list')
    return result