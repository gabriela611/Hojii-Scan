from xhtml2pdf import pisa
import io

class PdfGenerator:
    def __init__(self, json_data):
        self.json_data = json_data

    def generate_pdf(self):
        # Crear el HTML simple
        html = f"""
        <h1>Hoja de Vida</h1>
        <p><strong>Nombre:</strong> {self.json_data['nombre']} {self.json_data['apellido']}</p>
        <p><strong>Email:</strong> {self.json_data['email']}</p>
        <p><strong>Documento:</strong> {self.json_data['documento']}</p>
        <p><strong>Género:</strong> {self.json_data['genero']}</p>
        <h2>Educación</h2>
        """
        for edu in self.json_data['educacion']:
            html += f"""
            <p><strong>{edu['tipo']}:</strong> {edu['titulo']} en {edu['institucion']}</p>
            <p>Desde {edu['fecha_inicio']} hasta {edu['fecha_fin']}</p>
            """

        # Convertir HTML a PDF
        result = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=result)
        
        if pisa_status.err:
            raise Exception('Error al generar el PDF')

        return result.getvalue()
