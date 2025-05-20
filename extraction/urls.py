from django.urls import path, include
from .views import upload_image, generate_resume
from django.urls import path
from . import views

urlpatterns = [
    path("upload/", upload_image, name="upload_image"),
    path("generate_resume/", views.generate_resume, name="generate_resume"),
    path("success/", views.success_view, name="success"),  # Nueva ruta para la página de éxito
    path('', views.extraction_view, name='extraction'),  # Define la vista y el nombre
]

