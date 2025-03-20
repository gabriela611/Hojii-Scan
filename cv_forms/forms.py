from django import forms
from .models import PersonalInfo, EducationInfo
from .models import WorkExperience
from django.forms import modelformset_factory

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ['nombre', 'apellido', 'email', 'documento']

class EducationInfoForm(forms.ModelForm):
    class Meta:
        model = EducationInfo
        fields = ['tipo', 'institucion', 'titulo', 'fecha_inicio', 'fecha_fin']
    
    def clean_tipo(self):
        tipo = self.cleaned_data.get('tipo')
        if not tipo:
            raise forms.ValidationError("Debe seleccionar un tipo de educación.")
        return tipo


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['puesto', 'empresa', 'responsabilidades', 'proyectos', 'fecha_inicio', 'fecha_fin']
WorkExperienceFormSet = modelformset_factory(WorkExperience, fields=['puesto', 'empresa', 'responsabilidades', 'proyectos', 'fecha_inicio', 'fecha_fin'], extra=1)