import os
from django.core.wsgi import get_wsgi_application

# Ajuste “meu_projeto” se você renomeou a pasta
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meu_projeto.settings")

application = get_wsgi_application()
