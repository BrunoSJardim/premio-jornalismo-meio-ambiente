from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    # públicas
    path('', views.home, name='home'),
    path('regulamento/', views.regulamento, name='regulamento'),
    path('contato/', views.contato, name='contato'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.fazer_logout, name='logout'),

    # cadastro de usuários (somente staff)
    path('cadastro/', views.cadastro_usuario, name='cadastro_usuario'),

    # submissão de trabalhos
    path('enviar/', views.enviar_trabalho, name='enviar_trabalho'),
    path('sucesso/', lambda request: render(request, 'trabalhos/sucesso.html'), name='trabalho_enviado'),

    # área do avaliador (NOVO FLUXO)
    path('avaliador/', views.painel_avaliador, name='painel_avaliador'),  # default categoria
    path('avaliador/<str:tipo>/', views.painel_avaliador, name='painel_avaliador_tipo'),
    path('avaliador/avaliar/<int:atribuicao_id>/', views.avaliar_trabalho, name='avaliar_trabalho'),

    # comissão organizadora
    path('comissao/ranking/', views.painel_comissao_ranking, name='painel_comissao_ranking'),
    path('comissao/ranking/<str:tipo>/', views.painel_comissao_ranking, name='painel_comissao_ranking_tipo'),

    # painel admin
    path('painel/', views.painel_admin, name='painel_admin'),
    path('painel/parecer/<int:trabalho_id>/', views.gerar_parecer_pdf, name='gerar_parecer_pdf'),

    # diagnóstico/testes
    path('teste-upload/', views.teste_upload),
    path('checar-storage/', views.checar_storage),
]
