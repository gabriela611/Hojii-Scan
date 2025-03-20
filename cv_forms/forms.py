from django import forms
from .models import PersonalInfo, EducationInfo

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ['nombre', 'apellido', 'email', 'documento']

class EducationInfoForm(forms.ModelForm):
    class Meta:
        model = EducationInfo
        fields = ['tipo', 'institucion', 'titulo', 'fecha_inicio', 'fecha_fin']