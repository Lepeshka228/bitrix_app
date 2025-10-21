import csv
import io
from crypt import methods

from django.contrib import messages
from django.db.models.expressions import result
from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from .forms import UploadForm
from integration_utils.bitrix24.functions import batch_api_call


# Create your views here.
@main_auth(on_cookies=True)
def contacts(request):

    but = request.bitrix_user_token

    # список контактов
    cont_list = but.call_list_method('crm.contact.list', {'select': ['ID', 'EMAIL', 'PHONE']})
    print(cont_list)

    # хеш по номеру тел и имэйл для проверки существования контакта
    emails_dict = {}
    phones_dict = {}
    for contact in cont_list:
        for e in contact.get('EMAIL', []):
            emails_dict[e.get('VALUE')] = contact['ID']
        for p in contact.get('PHONE', []):
            phones_dict[p.get('VALUE')] = contact['ID']
    # список компаний
    company_list = but.call_list_method('crm.company.list', {'select': ['ID', 'TITLE']})
    # хеш по названию компании
    companies = {comp['TITLE']: comp['ID'] for comp in company_list}
    print(companies)
    # for contact in cont_list:
    #     comp_cont_list = but.call_list_method('crm.contact.company.items.get', {'id': contact['ID']})
    #     print(f"{contact['ID']}, {contact['NAME']} {contact['LAST_NAME']} компания - {contact['COMPANY_TITLE']}")


    form = UploadForm()
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            # проверяю расширение (оно должно быть csv)
            if not file.name.endswith('.csv'):
                messages.error(request, 'Это не CSV файл')
                return render(request, 'app5_contacts/contacts.html', {'form': form})

            # создаю список словарей - каждый словарь это контакт:
            # {'имя': 'Иван', 'фамилия': 'Иванов', 'номер телефона': '+79991234567',
            #   'почта': 'ivanov@example.com', 'компания': 'ООО "Ромашка"'}

            data_set = file.read().decode('utf-8')
            io_string = io.StringIO(data_set)
            reader = csv.DictReader(io_string, delimiter=',')

            methods = []
            errors = []
            for row in reader:
                first_name = row.get('имя', '').strip()
                last_name = row.get('фамилия', '').strip()
                phone = row.get('номер телефона', '').strip()
                email = row.get('почта', '').strip()
                company_name = row.get('компания', '').strip()

                # получаю id компании по названию
                company_id = companies.get(company_name)
                if not company_id:
                    errors.append(f"Компания '{company_name}' не найдена, создайте её, контакт {first_name} {last_name} не создан.")
                    continue  # не создаю этот контакт - пусть пользователь добавит компанию

                # проверка существующего контакта
                if (email and email in emails_dict) or (phone and phone in phones_dict):
                    errors.append(f"Контакт {first_name} {last_name} с таким email или телефоном уже существует.")
                    continue

                fields = {
                    "NAME": first_name,
                    "LAST_NAME": last_name,
                    "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}] if phone else [],
                    "EMAIL": [{"VALUE": email, "VALUE_TYPE": "WORK"}] if email else [],
                    "COMPANY_ID": company_id,  # Bitrix сам матчит по названию, если используется этот ключ
                }

                methods.append(("crm.contact.add", {"fields": fields}))

            # добавляю контакты
            try:
                result = but.batch_api_call(methods)

                successes = len(result.successes)
                errors_count = len(result.errors)
                messages.success(request, f'Создано контактов: {successes}, ошибок: {errors_count}')
                print("=========Ошибки batch=========:")
                for key, err in result.errors.items():
                    print(f"{key}: {err}")
            except Exception as e:
                messages.error(request, f'Ошибка при создании контактов: {e}')

            messages.success(request, 'Файл успешно загружен')
            return render(request, 'app5_contacts/contacts.html', {'form': form, 'errors': errors})

    return render(request, 'app5_contacts/contacts.html', {'form': form})