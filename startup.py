import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_projeto.settings.prod')
django.setup()

from trabalhos.models import Usuario
from django.db.utils import IntegrityError

email = 'brunodossantosjardim@gmail.com'
senha = 'Bj101200'  # Altere conforme necessário

try:
    if not Usuario.objects.filter(email=email).exists():
        Usuario.objects.create_superuser(email=email, nome='Bruno', senha=senha)
        print("Superusuário criado com sucesso.")
    else:
        print("Superusuário já existe.")
except IntegrityError as e:
    print("Erro ao criar superusuário:", e)

