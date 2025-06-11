from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Count
from django.template.loader import get_template
from django.utils.text import slugify
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail

from .models import Trabalho, Avaliacao
from .forms import CadastroUsuarioForm, TrabalhoForm, AvaliacaoForm
from meu_projeto.utils import salvar_arquivo

import io
from xhtml2pdf import pisa


# --- Views públicas e utilitárias ---

def home(request):
    return render(request, 'trabalhos/home.html')

def regulamento(request):
    return render(request, 'trabalhos/regulamento.html')

def contato(request):
    return render(request, 'trabalhos/contato.html')

def fazer_logout(request):
    logout(request)
    return redirect('home')


# --- Autenticação ---

def login_usuario(request):
    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['senha']
        user = authenticate(request, username=email, password=senha)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('painel_admin')
            elif user.tipo == 'autor':
                return redirect('enviar_trabalho')
            elif user.tipo == 'avaliador':
                return redirect('avaliar_trabalhos')
        messages.error(request, 'Email ou senha inválidos')
    return render(request, 'trabalhos/login.html')


@staff_member_required
def cadastro_usuario(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['senha'])
            user.is_active = True
            user.save()
            return redirect('painel_admin')
    else:
        form = CadastroUsuarioForm()
    return render(request, 'trabalhos/cadastro.html', {'form': form})


# --- Submissão e avaliação ---

def enviar_trabalho(request):
    if request.method == 'POST':
        form = TrabalhoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                trabalho = form.save()

                # Enviar e-mail de confirmação

                if trabalho.email:
                    send_mail(
                        subject='Confirmação de Inscrição - Prêmio SEMA',
                        message=(
                            f'Olá {trabalho.nome_completo},\n\n'
                            'Sua inscrição no Prêmio SEMA foi recebida com sucesso.\n'
                            'Agradecemos sua participação!'
                        ),
                        from_email=None,  # Usa DEFAULT_FROM_EMAIL do settings.py
                        recipient_list=[trabalho.email],
                        fail_silently=False,
                    )

                messages.success(request, "Trabalho enviado com sucesso.")
                return redirect('home')

            except Exception as e:
                messages.error(request, f"Erro ao salvar ou enviar e-mail: {e}")
        else:
            messages.error(request, "Formulário inválido.")
    else:
        form = TrabalhoForm()
    
    return render(request, 'trabalhos/enviar_trabalho.html', {'form': form})


@login_required
def avaliar_trabalhos(request):
    trabalhos = Trabalho.objects.all()
    avaliacoes_ids = Avaliacao.objects.filter(avaliador=request.user).values_list('trabalho_id', flat=True)
    return render(request, 'trabalhos/avaliar_trabalhos.html', {
        'trabalhos': trabalhos,
        'avaliacoes_ids': avaliacoes_ids,
    })


@login_required
def avaliar_trabalho(request, trabalho_id):
    trabalho = get_object_or_404(Trabalho, id=trabalho_id)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.trabalho = trabalho
            avaliacao.avaliador = request.user
            avaliacao.save()
            gerar_parecer_final(trabalho)
            return redirect('avaliar_trabalhos')
    else:
        form = AvaliacaoForm()
    return render(request, 'trabalhos/avaliar_formulario.html', {'form': form, 'trabalho': trabalho})


def gerar_parecer_final(trabalho):
    avaliacoes = Avaliacao.objects.filter(trabalho=trabalho)
    if avaliacoes.exists():
        counts = avaliacoes.values_list('recomendacao', flat=True)
        trabalho.parecer_final = (
            'Aceito' if list(counts).count('aceitar') > max(list(counts).count('rejeitar'), list(counts).count('revisar'))
            else 'Rejeitado' if list(counts).count('rejeitar') > list(counts).count('revisar')
            else 'Revisão necessária'
        )
        trabalho.save()


# --- Painel administrativo ---

@staff_member_required
def painel_admin(request):
    trabalhos = Trabalho.objects.all()
    status = request.GET.get('status')
    parecer = request.GET.get('parecer')
    busca = request.GET.get('busca')

    if status == 'submetido':
        trabalhos = trabalhos.annotate(num_avaliacoes=Count('avaliacao')).filter(num_avaliacoes=0)
    elif status == 'avaliado':
        trabalhos = trabalhos.annotate(num_avaliacoes=Count('avaliacao')).filter(num_avaliacoes__gt=0)

    if parecer:
        trabalhos = trabalhos.filter(avaliacao__recomendacao=parecer).distinct()

    if busca and busca.strip():
        trabalhos = trabalhos.filter(
            Q(titulo__icontains=busca) | Q(nome_completo__icontains=busca)
        )

    return render(request, 'trabalhos/painel_admin.html', {
        'trabalhos': trabalhos,
        'status_atual': status or '',
        'parecer_atual': parecer or '',
        'busca_atual': busca or '',
    })


@staff_member_required
def gerar_parecer_pdf(request, trabalho_id):
    trabalho = get_object_or_404(Trabalho, id=trabalho_id)
    template = get_template('trabalhos/parecer_pdf.html')
    html = template.render({'trabalho': trabalho})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="parecer_{slugify(trabalho.titulo)}.pdf"'
    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=response)
    return response if not pisa_status.err else HttpResponse('Erro ao gerar o PDF', status=500)


# --- Testes e diagnóstico ---

@staff_member_required
def teste_upload(request):
    try:
        path = 'teste_upload_final.txt'
        content = ContentFile("Arquivo com ACL pública garantida.".encode("utf-8"))
        url = salvar_arquivo(path, content)
        return HttpResponse(f"Arquivo enviado com sucesso: <a href='{url}' target='_blank'>{url}</a>")
    except Exception as e:
        return HttpResponse(f"Erro: {e}", status=500)


@staff_member_required
def checar_storage(request):
    tipo = type(default_storage).__name__
    caminho = settings.DEFAULT_FILE_STORAGE
    return HttpResponse(f"Storage em uso: {tipo}<br>DEFAULT_FILE_STORAGE: {caminho}")



