from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.functions import batch_api_call

from .forms import UploadForm
from . import services


@main_auth(on_cookies=True)
def contacts(request):
    but = request.bitrix_user_token

    # получаю существующие контакты через batch
    contacts_result = but.batch_api_call([('all_contacts', 'crm.contact.list', {'select': ['ID', 'EMAIL', 'PHONE']})])
    cont_list = contacts_result.successes.get('all_contacts', {}).get('result', [])

    existing_contacts = {'emails': {}, 'phones': {}}
    for contact in cont_list:
        for e in contact.get('EMAIL', []):
            existing_contacts['emails'][e.get('VALUE')] = contact['ID']
        for p in contact.get('PHONE', []):
            existing_contacts['phones'][p.get('VALUE')] = contact['ID']

    # получаю компании через batch
    companies_result = but.batch_api_call([('all_companies', 'crm.company.list', {'select': ['ID', 'TITLE']})])
    company_list = companies_result.successes.get('all_companies', {}).get('result', [])
    companies = {comp['TITLE']: comp['ID'] for comp in company_list}

    form = UploadForm()
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                contacts_file_data = services.parse_file(request.FILES['file'])
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'app5_contacts/contacts.html', {'form': form})

            methods, errors = services.prepare_contacts_for_import(contacts_file_data, existing_contacts, companies)

            successes = 0
            if methods:
                result = but.batch_api_call(methods)
                successes = len(result.successes)
                # ошибки batch
                for k, v in result.errors.items():
                    errors.append(f"{k}: {v}")

            if successes:
                messages.success(request, f'Создано контактов: {successes}, ошибок: {len(errors)}')
            else:
                messages.info(request, f'Ни один контакт не создан, ошибок: {len(errors)}')

            for err in errors:
                messages.error(request, err)

            return render(request, 'app5_contacts/contacts.html', {'form': form})

    return render(request, 'app5_contacts/contacts.html', {'form': form})


@main_auth(on_cookies=True)
def export_contacts(request, fmt='csv'):
    but = request.bitrix_user_token

    # получаем контакты и компании через batch
    batch_methods = [
        ('all_contacts', 'crm.contact.list', {'select': ['ID', 'NAME', 'LAST_NAME', 'PHONE', 'EMAIL', 'COMPANY_ID']}),
        ('all_companies', 'crm.company.list', {'select': ['ID', 'TITLE']})
    ]
    result = but.batch_api_call(batch_methods)

    contacts_list = result.successes.get('all_contacts', {}).get('result', [])
    company_list = result.successes.get('all_companies', {}).get('result', [])
    companies = {comp['ID']: comp['TITLE'] for comp in company_list}

    if fmt == 'csv':
        return services.contacts_to_csv_response(contacts_list, companies)
    else:
        return services.contacts_to_xlsx_response(contacts_list, companies)
