import sys
from pathlib import Path
import environ

from django.contrib import staticfiles
from dotenv import load_dotenv
import os

from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv('.env')
secret_key: str = os.getenv('secret_key')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['cityvoting.azurewebsites.net', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://cityvoting.azurewebsites.net']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'city_voting_registration',
    'city_map',
    'homepage',
    'voting',
    'user_submissions',
    'admin_panel',
    'help_and_support',
    'swagger',
    'drf_yasg',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'CityVotingPlatform.middleware.TracingMiddleware',
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'CityVotingPlatform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
storage_key: str = os.getenv('storage_key')
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_config")
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        'BACKEND': 'storages.backends.azure_storage.AzureStorage',
        'AZURE_ACCOUNT_NAME': 'cityvotingstorageaccount',
        'AZURE_ACCOUNT_KEY': storage_key,
        'AZURE_CONTAINER': 'profpicscont',
    },
}

AZURE_ACCOUNT_NAME = 'cityvotingstorageaccount'
AZURE_ACCOUNT_KEY = storage_key
AZURE_CONTAINER = 'profpicscont'

STATIC_HOST = os.environ.get("DJANGO_STATIC_HOST", "")
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static", ]

WSGI_APPLICATION = 'CityVotingPlatform.wsgi.application'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Database
db_password: str = os.getenv('db_password')

environ.Env.DB_SCHEMES['mssql'] = 'mssql'
env = environ.Env(DEBUG=(bool, False))
DEFAULT_DATABASE_URL = (
    f'mssql://krato:{db_password}@new-citivoting-db-server.database.windows.net/new-cityvoting-db?driver=ODBC'
    '+Driver+17+for+SQL+Server')

CONN_MAX_AGE = 20

DATABASE_URL = os.environ.get('DATABASE_URL', DEFAULT_DATABASE_URL)
os.environ['DJANGO_DATABASE_URL'] = DATABASE_URL.format(**os.environ)

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    DATABASES = {
        'default': env.db('DJANGO_DATABASE_URL', default=DEFAULT_DATABASE_URL)
    }
# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID
SITE_ID = 5

# Social authentication settings
SOCIALACCOUNT_LOGIN_ON_GET = True

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Redirect URLs after login and logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

LOGIN_URL = '/'

# Welcome email configurations
passwrd: str = os.getenv('passwrd')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'vebvebenko@gmail.com'
EMAIL_HOST_PASSWORD = passwrd
EMAIL_USE_TLS = True

# Application Insights
exporter = AzureMonitorTraceExporter(connection_string=os.getenv('app_insights_conn_str'))

tracer_provider = TracerProvider(resource=Resource.create({}),)
tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

DjangoInstrumentor().instrument()
LoggingInstrumentor().instrument()
trace.set_tracer_provider(tracer_provider)

# Swagger
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        }
    }
}

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'Accept',
    'Accept-Language',
    'Content-Language',
    'Content-Type',
    'Authorization',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny'
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

