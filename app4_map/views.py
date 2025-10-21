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
    address_list = api_inf['address_list']

    # хеши
    company_list_by_id = {int(comp['ID']): comp for comp in company_list}
    address_list_by_id = {int(addr['ENTITY_ID']): addr for addr in address_list}

    result = {}
    for company_id, company in company_list_by_id.items():
        addr = address_list_by_id.get(company_id, {})
        full_address_name = ", ".join(
            filter(None, [
                addr.get('ADDRESS_1'),
                addr.get('ADDRESS_2'),
                addr.get('CITY'),
                addr.get('REGION'),
                addr.get('PROVINCE'),
                addr.get('COUNTRY'),
            ])
        )
        result[company_id] = {'name': company["TITLE"], 'address': full_address_name}

    # JSON для передачи в шаблон
    result_json = json.dumps(result, ensure_ascii=False)
    # external_url для перехода
    result_encoded = urllib.parse.quote(result_json)
    external_url = f'http://localhost:3000/test/?data={result_encoded}'

    return render(request, 'app4_map/map.html', {
        'result_json': result_json,
        'external_url': external_url,
    })


def external_map(request):
    return render(request, 'app4_map/external_map.html')