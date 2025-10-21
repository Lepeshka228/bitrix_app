import csv
import io

from django.contrib import messages
from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from .forms import UploadForm


# Create your views here.
@main_auth(on_cookies=True)
def contacts(request):

    form = UploadForm()

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            # проверяю расширение (оно должно быть csv)
            if not file.name.endswith('.csv'):
                messages.error(request, 'Это не CSV файл')
                return render(request, 'app5_contacts/contacts.html', {'form': form})

            data_set = file.read().decode('utf-8')
            io_string = io.StringIO(data_set)
            reader = csv.reader(io_string, delimiter=',')

            messages.success(request, 'Файл успешно загружен')
            return render(request, 'app5_contacts/contacts.html', {'form': form})

    return render(request, 'app5_contacts/contacts.html', {'form': form})