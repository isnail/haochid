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