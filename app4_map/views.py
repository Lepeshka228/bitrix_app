from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from .services import api_info


# Create your views here.

@main_auth(on_cookies=True)
def map(request):
    but = request.bitrix_user_token
    api_inf = api_info(but)
    company_list = api_inf['company_list']
    # хеш по id
    company_list_by_id = {int(comp['ID']): comp for comp in company_list}
    print(company_list_by_id)
    address_list = api_inf['address_list']
    # хеш по entity_id
    address_list_by_id = {int(addr['ENTITY_ID']): addr for addr in address_list}
    print(address_list)
    for company_id, company in company_list_by_id.items():
        print(f'{company["TITLE"]} по адресу {address_list_by_id[company_id]["ADDRESS_1"]}')

    return render(request, 'app4_map/map.html', locals())

