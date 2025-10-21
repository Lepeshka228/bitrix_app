import json
import urllib.parse

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

    address_list = api_inf['address_list']
    # хеш по entity_id
    address_list_by_id = {int(addr['ENTITY_ID']): addr for addr in address_list}

    result = {}
    for company_id, company in company_list_by_id.items():
        full_address_name = (f"{(address_list_by_id.get(company_id) or {}).get('ADDRESS_1') or ''}, "
                             f"{(address_list_by_id.get(company_id) or {}).get('ADDRESS_2') or ''}, "
                             f"{(address_list_by_id.get(company_id) or {}).get('CITY') or ''}, "
                             f"{(address_list_by_id.get(company_id) or {}).get('REGION') or ''}, "
                             f"{(address_list_by_id.get(company_id) or {}).get('PROVINCE') or ''}, "
                             f"{(address_list_by_id.get(company_id) or {}).get('COUNTRY') or ''}")
        result[company_id] = {'name': company["TITLE"], 'address': full_address_name}
        result_json = urllib.parse.quote(json.dumps(result))
        external_url = f'http://localhost:3000/test/?data={result_json}'
    return render(request, 'app4_map/map.html', {'result': result, 'external_url': external_url})


def external_map(request):
    return render(request, 'app4_map/external_map.html')