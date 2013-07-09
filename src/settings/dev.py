__author__ = 'biyanbing'
from base import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'haochid',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
access_id = 'NtKMKCiLAiK8OlpV'
secret_access_key = 'Y6DEQhEhzgRzOJES5HdQZUFFj0rRsM'
oss_host = 'oss.aliyuncs.com'
bucket = 'haochid'

MEDIA_URL = 'http://%s/%s/' % (oss_host, bucket, )
STATIC_ROOT = '%s' % rel_path('../static')

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'


ALLOWED_HOSTS = ['hao.com']
BACKEND_LOG_FILE = 'django.log'
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
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
            },
        'file':{
            'level':'ERROR',
            'class':'logging.FileHandler',
            'filename': BACKEND_LOG_FILE,
            'formatter': 'verbose'
            },
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
        'meme.bg': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            },
        }
    }