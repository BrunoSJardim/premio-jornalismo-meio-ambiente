import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_projeto.settings.prod')
django.setup()

User = get_user_model()

email = "brunodossantosjardim@gmail.com"
senha = "Bj101200"
nome = "Bruno Jardim"

# Deleta usuário anterior com mesmo e-mail (se houver)
User.objects.filter(email=email).delete()

# Cria superusuário com todos os campos obrigatórios
User.objects.create_superuser(email=email, password=senha, nome=nome)

# Log para confirmar
print("Superusuário criado com sucesso!")
