from django import forms
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
            'status': forms.HiddenInput(), # Corrige o erro do campo "status" no formulário
        }

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

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario', 'recomendacao']
        widgets = {
            'nota': forms.NumberInput(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recomendacao': forms.Select(attrs={'class': 'form-select'}),
        }
