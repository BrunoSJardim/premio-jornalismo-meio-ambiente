from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .forms import CadastroUsuarioForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
import io
from .forms import TrabalhoForm
from .models import Trabalho, Avaliacao
from .models import Avaliacao
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Count
from django.contrib.auth import logout

def home(request):
    return render(request, 'trabalhos/home.html')

def regulamento(request):
    return render(request, 'trabalhos/regulamento.html')

def contato(request):
    return render(request, 'trabalhos/contato.html')    

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

def login_usuario(request):
    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['senha']
        user = authenticate(request, username=email, password=senha)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('painel_admin')
            elif user.tipo == 'autor':
                return redirect('enviar_trabalho')
            elif user.tipo == 'avaliador':
                return redirect('avaliar_trabalhos')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Email ou senha inválidos')

    return render(request, 'trabalhos/login.html')

@csrf_exempt
def enviar_trabalho(request):
    if request.method == 'POST':
        form = TrabalhoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TrabalhoForm()
    return render(request, 'trabalhos/enviar_trabalho.html', {'form': form})

@login_required
def avaliar_trabalhos(request):
    trabalhos = Trabalho.objects.all()
    avaliacoes = Avaliacao.objects.filter(avaliador=request.user)
    avaliacoes_ids = avaliacoes.values_list('trabalho_id', flat=True)

    return render(request, 'trabalhos/avaliar_trabalhos.html', {
        'trabalhos': trabalhos,
        'avaliacoes_ids': avaliacoes_ids,
    })

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario', 'recomendacao']

@login_required
def avaliar_trabalho(request, trabalho_id):
    trabalho = Trabalho.objects.get(id=trabalho_id)
    
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
        aceitar = avaliacoes.filter(recomendacao='aceitar').count()
        rejeitar = avaliacoes.filter(recomendacao='rejeitar').count()
        revisar = avaliacoes.filter(recomendacao='revisar').count()

        # Determina o parecer com base no maior número de recomendações
        
        if aceitar > rejeitar and aceitar > revisar:
            trabalho.parecer_final = 'Aceito'
        elif rejeitar > aceitar and rejeitar > revisar:
            trabalho.parecer_final = 'Rejeitado'
        else:
            trabalho.parecer_final = 'Revisão necessária'
        
        trabalho.save()
    
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def painel_admin(request):

    # Começamos com todos os trabalhos

    trabalhos = Trabalho.objects.all()

    # Captura dos parâmetros de filtro vindos na querystring
        
    status = request.GET.get('status')
    parecer = request.GET.get('parecer')
    busca = request.GET.get('busca')

    # 1) FILTRO POR STATUS
    #   - “submetido” = trabalhos sem NENHUMA avaliação
    #   - “avaliado” = trabalhos com 1 ou mais avaliações

    if status == 'submetido':

        # Filtra trabalhos cuja quantidade de avaliações seja igual a zero

        trabalhos = trabalhos.annotate(num_avaliacoes=Count('avaliacao')) \
                             .filter(num_avaliacoes=0)
    elif status == 'avaliado':

        # Filtra trabalhos cuja quantidade de avaliações seja maior que zero

        trabalhos = trabalhos.annotate(num_avaliacoes=Count('avaliacao')) \
                             .filter(num_avaliacoes__gt=0)
    
    # 2) FILTRO POR PARECER (baseado em Avaliacao.recomendacao)
    #    Filtra trabalhos que tenham pelo menos 1 avaliação cuja recomendação bate com o filtro

    if parecer:
        trabalhos = trabalhos.filter(avaliacao__recomendacao=parecer).distinct()

    # 3) FILTRO DE BUSCA (título ou nome completo)
    
    if busca and busca.strip() != '':
        trabalhos = trabalhos.filter(
            Q(titulo__icontains=busca) |
            Q(nome_completo__icontains=busca)
        )

    # Passa ao template tanto a lista já filtrada quanto os parâmetros atuais

    return render(request, 'trabalhos/painel_admin.html', {
        'trabalhos': trabalhos,
        'status_atual': status or '',
        'parecer_atual': parecer or '',
        'busca_atual': busca or '',
    })

@staff_member_required
def gerar_parecer_pdf(request, trabalho_id):
    trabalho = Trabalho.objects.get(id=trabalho_id)
    template = get_template('trabalhos/parecer_pdf.html')
    html = template.render({'trabalho': trabalho})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="parecer_{trabalho.id}.pdf"'
    
    pisa_status = pisa.CreatePDF(
        io.BytesIO(html.encode('utf-8')),
        dest=response,
        encoding='utf-8'
    )
    
    if pisa_status.err:
        return HttpResponse('Erro ao gerar o PDF', status=500)
    return response

def fazer_logout(request):
    logout(request)
    return redirect('home')


