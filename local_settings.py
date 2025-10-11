# настройки локального приложения
import os

DEBUG = True
ALLOWED_HOSTS = ['*']

from integration_utils.bitrix24.local_settings_class import LocalSettingsClass

TINKOFF_API_KEY = 'your-api-key'
ENDPOINT_TINKOFF = 'your-secret-key'
API_KEY_TINKOFF = 'your-api-key'
SECRET_KEY_TINKOFF = 'your-secret-key'

OPEN_AI_API_KEY = 'your-api-key'


APP_SETTINGS = LocalSettingsClass(
    portal_domain='b24-3vsj5n.bitrix24.ru',
    app_domain='127.0.0.1:8000',
    app_name='bitrix_app',
    salt=os.getenv('AS_SALT'),
    secret_key=os.getenv('AS_SECRETKEY'),
    application_bitrix_client_id=os.getenv('AS_CLIENT_ID'),
    application_bitrix_client_secret=os.getenv('AS_CLIENT_SECRET'),
    application_index_path='/',
)

NGROK_URL = 'https://mesothoracic-staidly-tena.ngrok-free.dev'
DOMAIN = NGROK_URL


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DATABASE_NAME'),  # Or path to database file if using sqlite3.
        'USER': os.getenv('DATABASE_USER'),  # Not used with sqlite3.
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),  # Not used with sqlite3.
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
    },
}