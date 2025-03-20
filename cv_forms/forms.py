from django import forms
from .models import PersonalInfo, EducationInfo

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ['nombre', 'apellido', 'email', 'documento']

class EducationInfoForm(forms.ModelForm):
    class Meta:
        model = EducationInfo
        fields = ['institucion', 'titulo', 'fecha_graduacion']