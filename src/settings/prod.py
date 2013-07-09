__author__ = 'biyanbing'
from base import *

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

DEBUG = False

import sae

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': sae.const.MYSQL_DB,
        'USER': sae.const.MYSQL_USER,
        'PASSWORD': sae.const.MYSQL_PASS,
        'HOST': sae.const.MYSQL_HOST,
        'PORT': sae.const.MYSQL_PORT,
    }
}

access_id = 'NtKMKCiLAiK8OlpV'
secret_access_key = 'Y6DEQhEhzgRzOJES5HdQZUFFj0rRsM'
oss_host = 'oss.aliyuncs.com'
bucket = 'haochid'

MEDIA_URL = 'http://haochid.oss.aliyuncs.com/'

ALLOWED_HOSTS = [
    'haochid.com',
    'haochid.sinaapp.com',
    'www.haochid.com'
]

ADMINS = ( ('iSnail', 'me@isnail.info'), )
MANAGERS = ADMINS

EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = '25'
EMAIL_HOST_USER = '18980692055@qq.com'
SERVER_EMAIL = 'service@haochid.com'
EMAIL_HOST_PASSWORD = 'see007'
EMAIL_SUBJECT_PREFIX = '[haochid] '
EMAIL_ADDRESS = SERVER_EMAIL

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s: %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
        'simple': {
            'format': '%(levelname)s: %(message)s'
            },
        },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
            }
        },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
            }
        },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
    }
