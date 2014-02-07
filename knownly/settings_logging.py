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
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'knownly.console.views': {
            'handlers':['console', 'mail_admins'],
            'level':'INFO',       
        },
        'knownly.console.middleware': {
            'handlers':['console', 'mail_admins'],
            'level':'WARN',       
        },
        'django.db.backends': {
            'handlers':['console', 'mail_admins'],
            'level':'ERROR',
        },
        'django.request': {
            'handlers':['console', 'mail_admins'],
            'level':'INFO',
        },
        'django': {
            'handlers':['console', 'mail_admins'],
            'level':'INFO',
        },
        'south': {
            'handlers':['console'],
            'level': 'ERROR',
        },
    },
}

from django.conf import settings
if settings.DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']
