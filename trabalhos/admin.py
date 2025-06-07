from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Trabalho, Avaliacao

class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'nome', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'nome')
    fieldsets = (
        (None, {'fields': ('email', 'nome', 'password')}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(Usuario, UsuarioAdmin)

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

