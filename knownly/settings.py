import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '&r$=!+FDIOSJVPSOIDVJ_*-wvf!tyf$asdfadfdfa(*_()*24132r1u'

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',
    'django_countries',
    'knownly.console',
    'knownly.billing',
    'knownly.landingpages',
    'knownly.plans',
)

MIDDLEWARE_CLASSES = (
    'knownly.console.middleware.SubdomainToDropboxMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'knownly.plans.middleware.CustomerPlanMiddleware'
)

ROOT_URLCONF = 'knownly.urls'

WSGI_APPLICATION = 'knownly.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Amsterdam'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'tmpl'),],
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

USE_I18N = True
USE_L10N = True
USE_TZ = True

INTERNAL_REDIRECT_DIRECTORY = 'dropbox_redirect'

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.SUCCESS: 'alert-success',
    message_constants.INFO: 'alert-info',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger',
}

CELERY_ACCEPT_CONTENT = ['json', ]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

try:
    from settings_local import *
except:
    print 'No settings_local.py available.'
    raise

try:
    from settings_logging import *
except:
    print 'Error loading logging configuration'
    raise

