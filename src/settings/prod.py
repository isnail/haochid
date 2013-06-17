__author__ = 'biyanbing'
from base import *

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

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

MEDIA_URL = 'http://images.haochid.com/'