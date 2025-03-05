from django.urls import path
from .views import extraction_view

urlpatterns = [
    path('', extraction_view, name='extraction'),
]