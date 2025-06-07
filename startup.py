import os
import django
from django.contrib.auth import get_user_model

# Define o módulo de configurações (ajuste se estiver em outro ambiente)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_projeto.settings.prod')
django.setup()

User = get_user_model()

email = "brunodossantosjardim@gmail.com"
senha = "Bj101020"
nome = "Bruno"

# Força a exclusão de superusuário existente com mesmo e-mail

User.objects.filter(email=email).delete()

# Cria novo superusuário

User.objects.create_superuser(email=email, password=senha, nome=nome)
print("Superusuário recriado com sucesso.")
