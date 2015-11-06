import os

import dj_database_url
from django.contrib.messages import constants as message_constants

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'django_nose',
    'django_countries',
    'rest_framework',
    'knownly.api',
    'knownly.console',
    'knownly.billing',
    'knownly.landingpages',
    'knownly.people',
    'knownly.plans',
)

INTERNAL_REDIRECT_DIRECTORY = 'dropbox_redirect'

MIDDLEWARE_CLASSES = (
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    'knownly.console.middleware.SubdomainToDropboxMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'knownly.plans.middleware.CustomerPlanMiddleware'
)

LANGUAGE_CODE = 'en-us'

ROOT_URLCONF = 'knownly.urls'

SECRET_KEY = '&r$=!+FDIOSJVPSOIDVJ_*-wvf!tyf$asdfadfdfa(*_()*24132r1u'

STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'tmpl'), ],
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

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

MESSAGE_TAGS = {
    message_constants.SUCCESS: 'alert-success',
    message_constants.INFO: 'alert-info',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger',
}

CELERY_ACCEPT_CONTENT = ['json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

try:
    from settings_local import *  # NOQA
except:
    print 'No settings_local.py available.'
    DATABASES = \
        {'default': dj_database_url.config(default=os.environ['DATABASE_URL'])}
    DEBUG = os.environ['DEBUG']
    DROPBOX_APP_KEY = os.environ['DROPBOX_APP_KEY']
    DROPBOX_APP_SECRET = os.environ['DROPBOX_APP_SECRET']
    MIXPANEL_TOKEN = os.environ['MIXPANEL_TOKEN']
    SECRET_KEY = os.environ['SECRET_KEY']
    STATIC_ROOT = os.environ['STATIC_ROOT']
    STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
    STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
    MASHAPE_API_KEY = os.environ['MASHAPE_API_KEY']
try:
    from settings_logging import *  # NOQA
except:
    print 'Error loading logging configuration'
    raise
