from django import forms
from .models import ScreenTimeEntry

# transforma o que o usuário digita em dados validados e prontos pra salvar no modelo,
# e também gera automaticamente o HTML do formulário.
class ScreenTimeEntryForm(forms.ModelForm):
    class Meta:
        model = ScreenTimeEntry
        fields = ['minutes', 'category', 'note']
        widgets = {
            'minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minutos'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observações (opcional)'
            }),
        }
