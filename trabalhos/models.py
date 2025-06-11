from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from storages.backends.s3boto3 import S3Boto3Storage


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError("O email deve ser fornecido.")
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nome, password, **extra_fields)


class PublicMediaStorage(S3Boto3Storage):
    default_acl = 'public-read'
    querystring_auth = False


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPOS_USUARIO = [
        ('admin', 'Administrador'),
        ('avaliador', 'Avaliador'),
    ]
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPOS_USUARIO, default='avaliador')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email


class Trabalho(models.Model):
    nome_completo = models.CharField(max_length=255)
    data_nascimento = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)

    banco = models.CharField(max_length=100, null=True, blank=True)
    agencia = models.CharField(max_length=20, null=True, blank=True)
    conta_corrente = models.CharField(max_length=20, null=True, blank=True)

    comprovante_bancario = models.FileField(
        storage=PublicMediaStorage, upload_to='comprovantes/', null=True, blank=True
    )
    registro_profissional = models.FileField(
        storage=PublicMediaStorage, upload_to='comprovantes/', null=True, blank=True
    )
    veiculo_universidade = models.FileField(
        storage=PublicMediaStorage, upload_to='comprovantes/', null=True, blank=True
    )

    CATEGORIAS = [
        ('jornalismo impresso', 'Jornalismo impresso'),
        ('webjornalismo', 'Webjornalismo'),
        ('fotojornalismo', 'Fotojornalismo'),
        ('radiojornalismo', 'Radiojornalismo'),
        ('telejornalismo', 'Telejornalismo'),
        ('jornalismo universitário', 'Jornalismo universitário'),
    ]
    categoria = models.CharField(max_length=24, choices=CATEGORIAS, null=True, blank=True)

    MICROTEMAS = [
        ('meio ambiente e desenvolvimento sustentável em sala de aula', 'Meio ambiente e desenvolvimento sustentável em sala de aula'),
        ('união de todos para o enfrentamento das mudanças climáticas', 'União de todos para o enfrentamento das mudanças climáticas'),
        ('mitigação no campo e as boas práticas já implementadas', 'Mitigação no campo e as boas práticas já implementadas'),
        ('uso consciente dos recursos hídricos no enfrentamento da estiagem', 'Uso consciente dos recursos hídricos no enfrentamento da estiagem'),
        ('energias limpas e renováveis para o desenvolvimento sustentável', 'Energias limpas e renováveis para o desenvolvimento sustentável'),
        ('ações de resiliência para um RS mais forte', 'Ações de resiliência para um RS mais forte'),
        ('soluções baseadas na natureza para promover a qualidade de vida da população', 'Soluções baseadas na natureza para promover a qualidade de vida da população'),
        ('recursos naturais do RS como potencial para o desenvolvimento econômico sustentável', 'Recursos naturais do RS como potencial para o desenvolvimento econômico sustentável'),
        ('nova vida: como estão os animais resgatados da enchente', 'Nova vida: como estão os animais resgatados da enchente'),
    ]
    microtema = models.CharField(max_length=83, choices=MICROTEMAS, null=True, blank=True)
    titulo = models.CharField(max_length=255, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    link_trabalho = models.URLField(blank=True, null=True)

    arquivo_trabalho = models.FileField(
        storage=PublicMediaStorage, upload_to='trabalhos/', blank=True, null=True
    )

    aceite_termo = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo or "(Sem título)"


class Avaliacao(models.Model):
    trabalho = models.ForeignKey('trabalhos.Trabalho', on_delete=models.CASCADE)
    avaliador = models.ForeignKey('trabalhos.Usuario', on_delete=models.CASCADE)
    nota = models.IntegerField()
    comentario = models.TextField()
    recomendacao = models.CharField(
        max_length=20,
        choices=[
            ('aceitar', 'Aceitar'),
            ('rejeitar', 'Rejeitar'),
            ('revisar', 'Revisar')
        ]
    )

    def __str__(self):
        return f"Avaliação de {self.trabalho} por {self.avaliador}"

