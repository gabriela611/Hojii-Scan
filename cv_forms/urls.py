from django.urls import path
from .views import personal_info_view, education_info_view

urlpatterns = [
    path('personal-info/', personal_info_view, name='personal_info'),
    path('education-info/', education_info_view, name='education_info'),
]