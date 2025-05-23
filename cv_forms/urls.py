from django.urls import path
from .views import personal_info_view, education_info_view
from .views import work_experience_view
from .views import habilidades_competencias_view
from .views import hoja_vida
from .views import generar_pdf

urlpatterns = [
    path('cv/personal-info/', personal_info_view, name='personal_info'),
    path('cv/education-info/', education_info_view, name='education_info'),
    path('work_experience/<int:personal_id>/', work_experience_view, name='work_experience'),
    path('habilidades/', habilidades_competencias_view, name='habilidades_competencias'),
    path('hoja_vida/<str:documento>/', hoja_vida, name='hoja_vida'),
     path('generar-pdf/<str:documento>/', generar_pdf, name='generar_pdf'),
]
