from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('regulamento/', views.regulamento, name='regulamento'),
    path('contato/', views.contato, name='contato'),
    path('cadastro/', views.cadastro_usuario, name='cadastro_usuario'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('enviar/', views.enviar_trabalho, name='enviar_trabalho'),
    path('sucesso/', lambda request: render(request, 'trabalhos/sucesso.html'), name='trabalho_enviado'),
    path('avaliar/', views.avaliar_trabalhos, name='avaliar_trabalhos'),
    path('avaliar/<int:trabalho_id>/', views.avaliar_trabalho, name='avaliar_trabalho'),
    path('painel/', views.painel_admin, name='painel_admin'),
    path('painel/parecer/<int:trabalho_id>/', views.gerar_parecer_pdf, name='gerar_parecer_pdf'),
    path("teste-upload/", views.teste_upload),
    path('logout/', views.fazer_logout, name='logout'),
]

