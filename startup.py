import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_projeto.settings.prod')

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
email = 'brunodossantosjardim@gmail.com'
senha = 'Bj101200'

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=senha)
    print(f"Superusuário '{email}' criado com sucesso.")
else:
    print(f"Superusuário '{email}' já existe.")