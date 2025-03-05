from django.urls import path
from .views import resume_form

urlpatterns = [
    path('', resume_form, name='resume_form'),
]