from django.urls import path
from .views import personal_info_view, education_info_view
from .views import work_experience_view

urlpatterns = [
    path('cv/personal-info/', personal_info_view, name='personal_info'),
    path('cv/education-info/', education_info_view, name='education_info'),
    path('work_experience/<int:personal_id>/', work_experience_view, name='work_experience'),

]
