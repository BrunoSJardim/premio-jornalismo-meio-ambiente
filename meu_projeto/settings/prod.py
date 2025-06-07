from .base import *
import dj_database_url

DEBUG = False
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1').split()

DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}
