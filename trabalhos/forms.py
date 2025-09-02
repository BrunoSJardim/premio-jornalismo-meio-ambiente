from django import forms
from .models import Avaliacao, NOTA_CHOICES
from .models import Trabalho, Usuario, Avaliacao

class TrabalhoForm(forms.ModelForm):
    class Meta:
        model = Trabalho
        fields = '__all__'   
        labels = {
            'registro_profissional': 'Registro profissional ou comprovante de matrícula',
            'veiculo_universidade': 'Veículo de imprensa ou universidade',
        }
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control'}),
            'conta_corrente': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_chave_pix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF / e-mail / celular / ...'}),
            'chave_pix': forms.TextInput(attrs={'class': 'form-control'}),
            'comprovante_bancario': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'registro_profissional': forms.TextInput(attrs={'class': 'form-control'}),
            'veiculo_universidade': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'microtema': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'link_trabalho': forms.URLInput(attrs={'class': 'form-control'}),
            'arquivo_trabalho': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'aceite_termo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = False       # ← evita erro de campo obrigatório
        self.fields['status'].widget = forms.HiddenInput()  # ← oculta o campo do HTML

class CadastroUsuarioForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_senha = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'confirmar_senha', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar = cleaned_data.get("confirmar_senha")

        if senha and confirmar and senha != confirmar:
            self.add_error('confirmar_senha', "As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        senha = self.cleaned_data.get('senha')
        user.set_password(senha)
        if commit:
            user.save()
        return user

class Radio1a7(forms.RadioSelect):
    pass  # usar assim por enquanto; adicionar depois um template custom;        

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = [
            'c_a_sensibilizacao_reflexao',
            'c_b_relacao_tema_microtemas',
            'c_c_info_tecnicas',
            'c_d_originalidade',
            'c_e_apresentacao',
            'comentario',
            'decisao',
        ]
        widgets = {
            'c_a_sensibilizacao_reflexao': Radio1a7(choices=NOTA_CHOICES),
            'c_b_relacao_tema_microtemas': Radio1a7(choices=NOTA_CHOICES),
            'c_c_info_tecnicas': Radio1a7(choices=NOTA_CHOICES),
            'c_d_originalidade': Radio1a7(choices=NOTA_CHOICES),
            'c_e_apresentacao': Radio1a7(choices=NOTA_CHOICES),
            'comentario': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'c_a_sensibilizacao_reflexao': 'a) Capacidade de sensibilização e reflexão (peso 5)',
            'c_b_relacao_tema_microtemas': 'b) Relação da pauta com o tema e microtemas (peso 4)',
            'c_c_info_tecnicas': 'c) Qualidade das informações técnicas (peso 3)',
            'c_d_originalidade': 'd) Originalidade no desenvolvimento (peso 2)',
            'c_e_apresentacao': 'e) Qualidade da apresentação (peso 1)',
        }
