# Django built-in loggers: django, django.request,
#                          django.db.backends, django.security.*

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s %(levelname)s %(module)s '
                      '%(process)d %(thread)d] %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s: %(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'WARNING',
            'class':
                'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'knownly.console.middleware': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',
            'propagate': False,
        },
        'knownly': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',
        },
        'django.db.backends': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
    },
}

from django.conf import settings

if settings.DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']
