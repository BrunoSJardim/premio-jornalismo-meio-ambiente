from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from storages.backends.s3boto3 import S3Boto3Storage


# =========================================
#  Usuário custom + Storage S3 (como o seu)
# =========================================

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
    # default_acl = None  # mantenha comentado se já ajustou via configuração
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


# ==================
#  Modelo: Trabalho
# ==================

class Trabalho(models.Model):
    # Dados pessoais
    nome_completo = models.CharField(max_length=255)
    data_nascimento = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)

    # Dados bancários
    banco = models.CharField(max_length=100, null=True, blank=True)
    agencia = models.CharField(max_length=20, null=True, blank=True)
    conta_corrente = models.CharField(max_length=20, null=True, blank=True)
    tipo_chave_pix = models.CharField(max_length=50, blank=True, null=True)
    chave_pix = models.CharField(max_length=100, blank=True, null=True)
    comprovante_bancario = models.FileField(
        storage=PublicMediaStorage(), upload_to='comprovantes/', null=True, blank=True
    )

    registro_profissional = models.CharField(max_length=100, null=True, blank=True)
    veiculo_universidade = models.CharField(max_length=100, null=True, blank=True)

    # Categoria e microtema
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

    # Conteúdo do trabalho
    titulo = models.CharField(max_length=255, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    link_trabalho = models.URLField(blank=True, null=True)
    arquivo_trabalho = models.FileField(
        storage=PublicMediaStorage(), upload_to='trabalhos/', null=True, blank=True
    )

    aceite_termo = models.BooleanField(default=False)

    STATUS_ESCOLHAS = [
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('rejeitado', 'Rejeitado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_ESCOLHAS, default='pendente')

    def __str__(self):
        return self.titulo or "(Sem título)"


# ==========================================
#   Atribuição (manual) e Avaliação objetiva
# ==========================================

# Tipos de júri
JURI_TIPOS = (
    ("categoria", "Júri de Categorias"),
    ("microtema", "Júri de Microtemas"),
)

# Decisões possíveis
DECISOES = (
    ("aceito", "Aceito"),
    ("rejeitado", "Rejeitado"),
    ("revisar", "Revisar"),
)

# Opções de nota (1..7)
NOTA_CHOICES = [(i, str(i)) for i in range(1, 8)]  # 1..7


class Atribuicao(models.Model):
    """
    Liga um Trabalho a um Avaliador para um TIPO DE JÚRI específico.
    A criação é manual via admin.
    """
    trabalho = models.ForeignKey(Trabalho, on_delete=models.CASCADE, related_name='atribuicoes')
    avaliador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='atribuicoes')
    tipo_juri = models.CharField(max_length=20, choices=JURI_TIPOS, default="categoria")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trabalho', 'avaliador', 'tipo_juri')  # evita duplicidade
        verbose_name = 'Atribuição'
        verbose_name_plural = 'Atribuições'

    def __str__(self):
        return f'{self.trabalho} → {self.avaliador} ({self.get_tipo_juri_display()})'


class Avaliacao(models.Model):
    """
    Parecer objetivo por marcações 1..7, com pesos fixos por critério.
    Uma avaliação por atribuição (OneToOne).
    """
    atribuicao = models.OneToOneField(Atribuicao, on_delete=models.CASCADE, related_name='avaliacao', null=True)

    # a) Capacidade de sensibilização e reflexão (PESO 5)
    c_a_sensibilizacao_reflexao = models.PositiveSmallIntegerField(
        choices=NOTA_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    # b) Relação da pauta com o tema e microtemas (PESO 4)
    c_b_relacao_tema_microtemas = models.PositiveSmallIntegerField(
        choices=NOTA_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    # c) Qualidade das informações técnicas (PESO 3)
    c_c_info_tecnicas = models.PositiveSmallIntegerField(
        choices=NOTA_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    # d) Originalidade (PESO 2)
    c_d_originalidade = models.PositiveSmallIntegerField(
        choices=NOTA_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    # e) Qualidade da apresentação (PESO 1)
    c_e_apresentacao = models.PositiveSmallIntegerField(
        choices=NOTA_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(7)]
    )

    comentario = models.TextField(blank=True)
    decisao = models.CharField(max_length=20, choices=DECISOES, default='revisar')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # Pesos usados na média ponderada
    PESOS = {
        "c_a_sensibilizacao_reflexao": 5,
        "c_b_relacao_tema_microtemas": 4,
        "c_c_info_tecnicas": 3,
        "c_d_originalidade": 2,
        "c_e_apresentacao": 1,
    }

    @property
    def soma_pesos(self):
        return sum(self.PESOS.values())  # 15

    @property
    def pontos_ponderados(self):
        return (
            self.c_a_sensibilizacao_reflexao * self.PESOS["c_a_sensibilizacao_reflexao"] +
            self.c_b_relacao_tema_microtemas * self.PESOS["c_b_relacao_tema_microtemas"] +
            self.c_c_info_tecnicas * self.PESOS["c_c_info_tecnicas"] +
            self.c_d_originalidade * self.PESOS["c_d_originalidade"] +
            self.c_e_apresentacao * self.PESOS["c_e_apresentacao"]
        )

    @property
    def media_ponderada(self):
        # normaliza para 1..7
        return round(self.pontos_ponderados / self.soma_pesos, 2)

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
