from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Count, Avg, Sum, F
from django.template.loader import get_template
from django.utils.text import slugify
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail

# MODELOS E FORMS (NOVO ESQUEMA)
from .models import Trabalho, Avaliacao, Atribuicao
from .forms import CadastroUsuarioForm, TrabalhoForm, AvaliacaoForm

# Utilitário opcional que você já usa
from meu_projeto.utils import salvar_arquivo

import io
from xhtml2pdf import pisa

# Fechar inscricoes
from django.http import HttpResponseForbidden


# ==============================
#  Views públicas e utilitárias
# ==============================

def home(request):
    return render(request, 'trabalhos/home.html')

def regulamento(request):
    return render(request, 'trabalhos/regulamento.html')

def contato(request):
    return render(request, 'trabalhos/contato.html')

def fazer_logout(request):
    logout(request)
    return redirect('home')


# ===============
#  Autenticação
# ===============

def login_usuario(request):
    """
    Redireciona:
      - superuser → painel_admin
      - avaliador → painel_avaliador (tipo padrão: categoria)
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        user = authenticate(request, username=email, password=senha)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('home')
            elif getattr(user, 'tipo', None) == 'avaliador':
                return redirect('painel_avaliador')
            # fallback
            return redirect('home')
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


# ==========================
#  Submissão de trabalhos
# ==========================

def enviar_trabalho(request):

    # controle simples (troque True/False quando quiser abrir/fechar)
    INSCRICOES_ABERTAS = True
    if not INSCRICOES_ABERTAS:
        return render(request, "trabalhos/inscricoes_encerradas.html")

    if request.method == 'POST':
        form = TrabalhoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                trabalho = form.save(commit=False)
                trabalho.status = 'pendente'  # força valor padrão
                trabalho.save()

                # E-mail de confirmação (opcional)
                if trabalho.email:
                    send_mail(
                        subject='Inscrição Confirmada - Prêmio SEMA-FEPAM de Jornalismo Ambiental 2025',
                        message=(
                            'Recebemos sua inscrição com sucesso no Prêmio SEMA-FEPAM de Jornalismo Ambiental 2025.\n\n'
                            'Atenciosamente,\nComissão Organizadora\n'
                        ),
                        from_email=None,  # usa DEFAULT_FROM_EMAIL
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


# ==========================
#  Área do Avaliador (NOVO)
# ==========================

@login_required
def painel_avaliador(request, tipo='categoria'):
    """
    Lista de TRABALHOS atribuídos ao avaliador logado para um tipo de júri.
    Trabalhamos sobre Atribuição (não mais Trabalho direto).
    """
    atribuicoes = (Atribuicao.objects
                   .select_related('trabalho')
                   .filter(avaliador=request.user, tipo_juri=tipo)
                   .order_by('-criado_em'))
    return render(request, 'trabalhos/avaliar_trabalhos.html', {
        'atribuicoes': atribuicoes,
        'tipo': tipo,
    })


@login_required
def avaliar_trabalho(request, atribuicao_id):
    """
    Preenchimento/edição do parecer objetivo (1..7) para uma ATRIBUIÇÃO.
    Garante que o avaliador só acesse o que foi atribuído para ele.
    """
    atribuicao = get_object_or_404(Atribuicao, id=atribuicao_id, avaliador=request.user)
    instance = getattr(atribuicao, 'avaliacao', None)

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=instance)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.atribuicao = atribuicao
            avaliacao.save()
            messages.success(request, 'Parecer salvo com sucesso.')
            return redirect('painel_avaliador_tipo', tipo=atribuicao.tipo_juri)
    else:
        form = AvaliacaoForm(instance=instance)

    return render(request, 'trabalhos/avaliar_formulario.html', {
        'form': form,
        'atribuicao': atribuicao,
    })


# ==================================================
#  Painel da Comissão — Ranking por tipo de júri
# ==================================================

@staff_member_required
def painel_comissao_ranking(request, tipo='categoria'):
    """
    Ranking por TRABALHO dentro de um tipo de júri, usando média ponderada (pesos 5,4,3,2,1).
    """
    qs = (Avaliacao.objects
          .filter(atribuicao__tipo_juri=tipo)
          .annotate(
              t_id=F('atribuicao__trabalho'),
              pontos=(F('c_a_sensibilizacao_reflexao') * 5 +
                      F('c_b_relacao_tema_microtemas') * 4 +
                      F('c_c_info_tecnicas') * 3 +
                      F('c_d_originalidade') * 2 +
                      F('c_e_apresentacao') * 1)
          )
          .values('t_id')
          .annotate(
              pontos_totais=Sum('pontos'),
              n_pareceres=Count('id'),
              media_ponderada=Avg(
                  (F('c_a_sensibilizacao_reflexao') * 5 +
                   F('c_b_relacao_tema_microtemas') * 4 +
                   F('c_c_info_tecnicas') * 3 +
                   F('c_d_originalidade') * 2 +
                   F('c_e_apresentacao') * 1) / 15.0
              ),
          )
          .order_by('-media_ponderada', '-pontos_totais'))

    return render(request, 'trabalhos/painel_comissao_ranking.html', {
        'tipo': tipo,
        'ranking': list(qs),
    })


# ==========================
#  Painel administrativo
# ==========================

@staff_member_required
def painel_admin(request):
    """
    Painel simples para a organização filtrar/consultar trabalhos.
    (Removido qualquer acoplamento à recomendação antiga.)
    """
    trabalhos = Trabalho.objects.all()
    status = request.GET.get('status')
    busca = request.GET.get('busca')

    if status == 'submetido':
        # sem nenhuma avaliação ainda (conta por Atribuições/Avaliações)
        trabalhos = trabalhos.annotate(num_atribs=Count('atribuicoes')).filter(num_atribs=0)
    elif status == 'atribuido':
        trabalhos = trabalhos.annotate(num_atribs=Count('atribuicoes')).filter(num_atribs__gt=0)

    if busca and busca.strip():
        trabalhos = trabalhos.filter(
            Q(titulo__icontains=busca) | Q(nome_completo__icontains=busca) | Q(email__icontains=busca)
        )

    return render(request, 'trabalhos/painel_admin.html', {
        'trabalhos': trabalhos,
        'status_atual': status or '',
        'busca_atual': busca or '',
    })


# ==========================
#  PDF de parecer (opcional)
# ==========================

@staff_member_required
def gerar_parecer_pdf(request, trabalho_id):
    """
    Gera um PDF com dados do trabalho + médias (se quiser, dá para expandir com
    as avaliações detalhadas).
    """
    trabalho = get_object_or_404(Trabalho, id=trabalho_id)
    template = get_template('trabalhos/parecer_pdf.html')
    html = template.render({'trabalho': trabalho})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="parecer_{slugify(trabalho.titulo or trabalho.id)}.pdf"'
    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=response)
    return response if not pisa_status.err else HttpResponse('Erro ao gerar o PDF', status=500)


# ==========================
#  Testes e diagnóstico
# ==========================

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
