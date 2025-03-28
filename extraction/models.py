from django.db import models

class ExtractedResume(models.Model):
    name = models.CharField(max_length=255)  # Nombre que el usuario elija
    pdf_file = models.FileField(upload_to='resumes/')  # Almacenar el PDF generado
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación

    def __str__(self):
        return self.name