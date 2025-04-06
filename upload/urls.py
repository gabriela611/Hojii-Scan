from django.urls import path
from .views import upload_resume, resume_list, generate_pdf, resume_preview, confirmation

urlpatterns = [
    path("", upload_resume, name="upload_resume"),
    path("resumes/", resume_list, name="resume_list"),
    path("preview/<int:resume_id>/", resume_preview, name="resume_preview"),
    path("generate-pdf/<int:resume_id>/", generate_pdf, name="generate_pdf"),
    path("confirmation/<int:resume_id>/", confirmation, name="confirmation"),
]