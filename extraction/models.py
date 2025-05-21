from django.db import models

class ExtractedResume(models.Model):
    # Información general
    name = models.CharField(max_length=255, null=True, blank=True)  # Nombre del archivo o referencia
    profession = models.CharField(max_length=255, null=True, blank=True)  # Profesión o puesto deseado
    pdf_file = models.FileField(upload_to='resumes/', null=True, blank=True)  # PDF generado
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Fecha de subida

    # Información personal
    GENERO_OPCIONES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('NB', 'No Binario'),
        ('O', 'Otro'),
        ('P', 'Prefiero no decirlo'),
    ]
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    documento = models.CharField(max_length=20, unique=True, null=True, blank=True)
    genero = models.CharField(max_length=2, choices=GENERO_OPCIONES, default='P', null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    # Habilidades y competencias
    habilidades_tecnicas = models.TextField(blank=True, null=True, help_text="Ejemplo: Python, SQL, Redes")
    cualidades_personales = models.TextField(blank=True, null=True, help_text="Ejemplo: Responsable, puntual, trabajo en equipo")
    idiomas = models.TextField(blank=True, null=True, help_text="Ejemplo: Español nativo, Inglés B1")
    trabajo_deseado = models.CharField(max_length=255, blank=True, null=True, help_text="Ejemplo: Desarrollador backend en Python")

    def str(self):
        return f"{self.nombre} {self.apellido} - {self.profession}"