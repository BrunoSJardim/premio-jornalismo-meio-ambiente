from .base import *

SECRET_KEY = 'chave-secreta-local'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'premiosema',
        'USER': 'semauser',
        'PASSWORD': 'senha1012',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
