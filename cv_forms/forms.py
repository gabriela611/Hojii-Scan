from django import forms
from .models import PersonalInfo, EducationInfo
from .models import WorkExperience
from django.forms import modelformset_factory
from .models import HabilidadesCompetencias

class PersonalInfoForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = PersonalInfo
        fields = ['nombre', 'apellido', 'email', 'documento', 'genero', 'fecha_nacimiento']
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-control'}),
        }

class EducationInfoForm(forms.ModelForm):
    class Meta:
        model = EducationInfo
        fields = ['tipo', 'institucion', 'titulo', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

WorkExperienceFormSet = modelformset_factory(
    WorkExperience,
    fields=['puesto', 'empresa', 'responsabilidades', 'proyectos', 'fecha_inicio', 'fecha_fin'],
    extra=1,
    widgets = {
            'puesto': forms.TextInput(attrs={'class': 'input-box'}),
            'empresa': forms.TextInput(attrs={'class': 'input-box'}),
            'responsabilidades': forms.Textarea(attrs={'class': 'input-box'}),
            'proyectos': forms.Textarea(attrs={'class': 'input-box'}),
        }
    
)


class HabilidadesCompetenciasForm(forms.ModelForm):
    class Meta:
        model = HabilidadesCompetencias
        fields = ['habilidades_tecnicas', 'cualidades_personales', 'idiomas', 'trabajo_deseado']
        widgets = {
            'habilidades_tecnicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cualidades_personales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'idiomas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'trabajo_deseado': forms.TextInput(attrs={'class': 'form-control'}),
        }