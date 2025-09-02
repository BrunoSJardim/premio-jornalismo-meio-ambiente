from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Usuario, Trabalho, Atribuicao, Avaliacao


# ==========================
#  Usuário (custom UserAdmin)
# ==========================
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ("email", "nome", "tipo", "is_staff", "is_active")
    list_filter = ("tipo", "is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email", "nome")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações pessoais", {"fields": ("nome", "tipo")}),
        ("Permissões", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nome", "tipo", "password1", "password2", "is_staff", "is_active"),
        }),
    )

admin.site.register(Usuario, UsuarioAdmin)


# ==========================================
#  Inlines
# ==========================================
class AtribuicaoInline(admin.TabularInline):
    """
    Atribuições (manual) direto na página do Trabalho.
    Permite vincular avaliadores e escolher o tipo de júri.
    """
    model = Atribuicao
    extra = 1
    autocomplete_fields = ("avaliador",)
    fields = ("avaliador", "tipo_juri", "criado_em")
    readonly_fields = ("criado_em",)


class AvaliacaoInline(admin.StackedInline):
    """
    Edita a Avaliação dentro da Atribuição (no máximo 1 por atribuição).
    """
    model = Avaliacao
    extra = 0
    can_delete = False
    fieldsets = (
        (None, {
            "fields": (
                ("c_a_sensibilizacao_reflexao", "c_b_relacao_tema_microtemas", "c_c_info_tecnicas"),
                ("c_d_originalidade", "c_e_apresentacao"),
                "comentario",
                "decisao",
            )
        }),
    )


# ==========================
#  Trabalho
# ==========================
@admin.register(Trabalho)
class TrabalhoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "nome_completo", "categoria", "microtema", "status", "email")
    list_filter = ("status", "categoria", "microtema")
    search_fields = ("titulo", "nome_completo", "email")
    inlines = [AtribuicaoInline]  # ← Inline solicitado


# ==========================================
#  Atribuição (manual) + Avaliação (inline)
# ==========================================
@admin.register(Atribuicao)
class AtribuicaoAdmin(admin.ModelAdmin):
    list_display = ("trabalho", "avaliador", "tipo_juri", "tem_avaliacao", "criado_em")
    list_filter = ("tipo_juri", "criado_em")
    search_fields = ("trabalho__titulo", "avaliador__nome", "avaliador__email")
    autocomplete_fields = ("trabalho", "avaliador")
    inlines = [AvaliacaoInline]

    def tem_avaliacao(self, obj):
        ok = hasattr(obj, "avaliacao")
        return format_html('<b style="color:{}">{}</b>',
                           "green" if ok else "crimson",
                           "Sim" if ok else "Não")
    tem_avaliacao.short_description = "Avaliado?"


# ==========================
#  Avaliação (admin dedicado)
# ==========================
@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("atribuicao", "get_tipo_juri", "media_ponderada", "decisao", "atualizado_em")
    list_filter = ("decisao", "atribuicao__tipo_juri", "atualizado_em")
    search_fields = ("atribuicao__trabalho__titulo", "atribuicao__avaliador__nome", "atribuicao__avaliador__email")
    readonly_fields = ("criado_em", "atualizado_em")
    fieldsets = (
        (None, {
            "fields": (
                "atribuicao",
                ("c_a_sensibilizacao_reflexao", "c_b_relacao_tema_microtemas", "c_c_info_tecnicas"),
                ("c_d_originalidade", "c_e_apresentacao"),
                "comentario",
                "decisao",
                ("criado_em", "atualizado_em"),
            )
        }),
    )

    def get_tipo_juri(self, obj):
        return obj.atribuicao.get_tipo_juri_display()
    get_tipo_juri.short_description = "Tipo de Júri"
