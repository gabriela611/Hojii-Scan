"""
URL configuration for HojiiScan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views  # Importamos la vista home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Página principal
    path('extraction/', include('extraction.urls')), # app de extracción de texto de foto
    path('upload/', include('upload.urls')), # app de subida de archivos
    path('resume/', include('resume.urls')),  # Nueva app de formulario
    
]
