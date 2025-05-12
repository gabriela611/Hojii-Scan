import json
from django.conf import settings
import os

class CvJsonBuilder:
    def __init__(self, personal_info):
        self.personal_info = personal_info

    def build(self):
        data = {
            'nombre': self.personal_info.nombre,
            'apellido': self.personal_info.apellido,
            'email': self.personal_info.email,
            'documento': self.personal_info.documento,
            'genero': self.personal_info.get_genero_display(),
            'fecha_nacimiento': str(self.personal_info.fecha_nacimiento),
            'educacion': [],
            'experiencia_laboral': [],
            'habilidades': {
                'habilidades_tecnicas': self.personal_info.habilidades.habilidades_tecnicas,
                'cualidades_personales': self.personal_info.habilidades.cualidades_personales,
                'idiomas': self.personal_info.habilidades.idiomas,
                'trabajo_deseado': self.personal_info.habilidades.trabajo_deseado,
            }
        }

        for edu in self.personal_info.education_info.all():
            data['educacion'].append({
                'tipo': edu.get_tipo_display(),
                'institucion': edu.institucion,
                'titulo': edu.titulo,
                'fecha_inicio': str(edu.fecha_inicio),
                'fecha_fin': str(edu.fecha_fin),
            })

        for exp in self.personal_info.work_experiences.all():
            data['experiencia_laboral'].append({
                'puesto': exp.puesto,
                'empresa': exp.empresa,
                'responsabilidades': exp.responsabilidades,
                'proyectos': exp.proyectos,
                'fecha_inicio': str(exp.fecha_inicio),
                'fecha_fin': str(exp.fecha_fin),
            })

        return data

    def save_to_file(self):
        data = self.build()
        path = os.path.join(settings.MEDIA_ROOT, 'cv_json')
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, f'{self.personal_info.documento}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return file_path
