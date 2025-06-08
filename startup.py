import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_projeto.settings.prod')
django.setup()

User = get_user_model()

email = "brunodossantosjardim@gmail.com"
senha = "Bj101200"
nome = "Bruno"

print("Ambiente configurado. ")

# user, created = User.objects.get_or_create(email=email, defaults={'nome': nome})
#if created:
    # user.set_password(senha)
    # user.is_staff = True
    # user.is_superuser = True
    # user.save()
    # print("Superusuário criado com sucesso.")
# else:
    # user.set_password(senha)
    # user.save()
    # print("Senha do superusuário atualizada com sucesso.")

