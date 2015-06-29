# Django built-in loggers: django, django.request, django.db.backends, django.security.*

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d] %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s: %(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level':'WARNING',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'WARNING',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'knownly.console.middleware': {
            'handlers':['console', 'mail_admins'],
            'level':'WARNING',
            'propagate': False,
        },
        'knownly': {
            'handlers':['console', 'mail_admins'],
            'level':'WARNING',
        },
        'django.db.backends': {
            'handlers':['console', 'mail_admins'],
            'level':'WARNING',
        },
        'django.request': {
            'handlers':['console', 'mail_admins'],
            'level':'WARNING',
        },
        'django': {
            'handlers':['console', 'mail_admins'],
            'level':'WARNING',
        },
    },
}

from django.conf import settings
if settings.DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']
