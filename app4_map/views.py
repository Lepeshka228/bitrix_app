from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from .services import api_info


# Create your views here.

@main_auth(on_cookies=True)
def map(request):
    but = request.bitrix_user_token
    api_inf = api_info(but)
    company_fields = api_inf['company_fields']
    print(company_fields)
    for key, value in company_fields.items():
        print(f"{key} ===== {value.get('title', [])}")
    return render(request, 'app4_map/map.html', locals())

