from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

@main_auth(on_cookies=True)
def deals(request):
    deals = {
        'Сделка 1': 'Информация по сделке 1',
        'Сделка 2': 'Информация по сделке 2',
    }
    return render(request, 'app1_deals/deals.html', locals())

@main_auth(on_cookies=True)
def reload_index(request):
    user_name = f'{request.bitrix_user.first_name} {request.bitrix_user.last_name}'
    return render(request, 'main/index.html', locals())