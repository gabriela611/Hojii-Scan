from xhtml2pdf import pisa
import io

class PdfGenerator:
    def __init__(self, json_data):
        self.json_data = json_data

    def generate_pdf(self):
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    font-size: 10pt;
                    color: #333;
                    line-height: 1;
                }}

                h1 {{
                    text-align: center;
                    color: #2E8B57;
                    border-bottom: 2px solid #2E8B57;
                    padding-bottom: 8px;
                    margin-bottom: 15px;
                    line-height: 1.1;
                }}

                h2 {{
                    color: #2E8B57;
                    margin-top: 20px;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 5px;
                    line-height: 1.1;
                }}

                p {{
                    margin: 0;
                    padding: 0;
                    line-height: 1;
                }}

                .section {{
                    margin-bottom: 12px;
                }}

                .empresa {{
                    color: #2E8B57;
                    font-weight: bold;
                    font-size: 11pt;
                    margin: 5px 0 3px 0;
                    line-height: 1.1;
                }}
            </style>
        </head>
        <body>
            <h1>Hoja de Vida</h1>

            <div class="section">
                <p><strong>Nombre:</strong> {self.json_data.get('nombre', '')} {self.json_data.get('apellido', '')}</p>
                <p><strong>Email:</strong> {self.json_data.get('email', '')}</p>
                <p><strong>Documento:</strong> {self.json_data.get('documento', '')}</p>
                <p><strong>Género:</strong> {self.json_data.get('genero', '')}</p>
                <p><strong>Fecha de nacimiento:</strong> {self.json_data.get('fecha_nacimiento', '')}</p>
            </div>

            <h2>Educación</h2>
        """
        for edu in self.json_data.get('educacion', []):
            html += f"""
            <div class="section">
                <p><strong>{edu.get('tipo', '')}:</strong> {edu.get('titulo', '')} en {edu.get('institucion', '')}</p>
                <p>Desde {edu.get('fecha_inicio', '')} hasta {edu.get('fecha_fin', '')}</p>
            </div>
            """

        html += "<h2>Experiencia Laboral</h2>"
        for exp in self.json_data.get('experiencia_laboral', []):
            html += f"""
            <div class="section">
                <p class="empresa">{exp.get('puesto', '')} en {exp.get('empresa', '')}</p>
                <p><strong>Responsabilidades:</strong> {exp.get('responsabilidades', '')}</p>
                <p><strong>Proyectos:</strong> {exp.get('proyectos', '')}</p>
                <p>Desde {exp.get('fecha_inicio', '')} hasta {exp.get('fecha_fin', '')}</p>
            </div>
            """

        habilidades = self.json_data.get('habilidades', {})
        html += """
        <h2>Habilidades</h2>
        <div class="section">
            <p>• <strong>Habilidades técnicas:</strong> {habilidades_tecnicas}</p>
            <p>• <strong>Cualidades personales:</strong> {cualidades_personales}</p>
            <p>• <strong>Idiomas:</strong> {idiomas}</p>
            <p>• <strong>Trabajo deseado:</strong> {trabajo_deseado}</p>
        </div>
        """.format(
            habilidades_tecnicas=habilidades.get('habilidades_tecnicas', ''),
            cualidades_personales=habilidades.get('cualidades_personales', ''),
            idiomas=habilidades.get('idiomas', ''),
            trabajo_deseado=habilidades.get('trabajo_deseado', '')
        )

        html += "</body></html>"

        result = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=result)

        if pisa_status.err:
            raise Exception('Error al generar el PDF')

        return result.getvalue()
