import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_projeto.settings.prod')
django.setup()

User = get_user_model()

email = "brunodossantosjardim@gmail.com"
senha = "Bj101200"
nome = "Bruno"

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=senha, nome=nome)
    print("Superusuário criado com sucesso.")
else:
    print("Superusuário já existe.")

