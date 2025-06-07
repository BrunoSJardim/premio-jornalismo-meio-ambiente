from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Trabalho, Avaliacao

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    model = Usuario
    list_display = ('email', 'nome', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('email', 'nome')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'nome', 'tipo')}),
        ('Permissões', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'tipo', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )

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

