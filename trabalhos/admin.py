from django.contrib import admin
from .models import Usuario, Trabalho, Avaliacao

@admin.register(Usuario)

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'is_staff', 'is_superuser')
    search_fields = ('e-mail', 'nome')
    list_filter = ('is_staff', 'is_superuser')

@admin.register(Trabalho)
class TrabalhoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', 'categoria')  
    list_filter = ('categoria',)  
    search_fields = ('nome_completo', 'email', 'titulo')

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('trabalho', 'avaliador', 'nota', 'recomendacao')
    search_fields = ('trabalho__titulo', 'avaliador__email')
    list_filter = ('recomendacao',)

