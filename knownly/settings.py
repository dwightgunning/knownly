import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '&r$=!+FDIOSJVPSOIDVJ_*-wvf!tyf$asdfadfdfa(*_()*24132r1u'

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'knownly.net', '.knownly.net']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'knownly.console',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'knownly.console.middleware.SubdomainToDropboxMiddleware',
)

ROOT_URLCONF = 'knownly.urls'

WSGI_APPLICATION = 'knownly.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Amsterdam'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'tmpl'),
)

USE_I18N = True
USE_L10N = True
USE_TZ = True

INTERNAL_REDIRECT_DIRECTORY = 'dropbox_redirect'

try:
    from settings_local import *
except:
    print 'No settings_local.py available.'
