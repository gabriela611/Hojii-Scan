from django.db import models


class PersonalInfo(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    documento = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class EducationInfo(models.Model):
    personal_info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE, related_name="education_info")
    TIPO_EDUCACION = [
        ('secundaria', 'Educación Secundaria'),
        ('universitaria', 'Educación Superior Universitaria'),
        ('posgrado', 'Educación de Posgrado'),
        ('otros', 'Otros estudios'),
    ]
    
    tipo = models.CharField(max_length=50, choices=TIPO_EDUCACION, default='secundaria')
    institucion = models.CharField(max_length=100, blank=True, null=True)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.personal_info.nombre} - {self.get_tipo_display()} - {self.titulo}"