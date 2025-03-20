from django.db import models

class PersonalInfo(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    documento = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class EducationInfo(models.Model):
    personal_info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE)
    institucion = models.CharField(max_length=255)
    titulo = models.CharField(max_length=255)
    fecha_graduacion = models.DateField()

    def __str__(self):
        return f"{self.titulo} en {self.institucion}"