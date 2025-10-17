from django import forms
from .models import ScreenTimeEntry

class ScreenTimeEntryForm(forms.ModelForm):
    hours = forms.IntegerField(
        required=False,
        min_value=0,
        label="Horas",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Horas'
        })
    )

    class Meta:
        model = ScreenTimeEntry
        fields = ['hours', 'minutes', 'category', 'note']
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

    def clean(self):
        cleaned_data = super().clean()
        hours = cleaned_data.get('hours') or 0
        minutes = cleaned_data.get('minutes') or 0
        cleaned_data['minutes'] = (hours * 60) + minutes
        return cleaned_data
