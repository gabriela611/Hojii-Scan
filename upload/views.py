import pdfplumber
import re
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UploadedResume
from reportlab.lib.pagesizes import letter
from io import BytesIO
from reportlab.pdfgen import canvas
import json
from django.urls import reverse

SECTION_TITLES = [
    "AREA OF EXPERTISE",
    "KEY ACHIEVEMENTS",
    "PROFESSIONAL EXPERIENCE",
    "EDUCATION",
    "ADDITIONAL INFORMATION"
]

def parse_education_block(education_lines):
    """
    Convierte las líneas de la sección EDUCATION en una lista de dicts,
    cada dict con {degree, institution, start_date, end_date, details}.
    Usamos un patrón de fechas 'Mes Año - Mes Año' para segmentar.
    """
    blocks = []
    current_block = {
        "degree": "",
        "institution": "",
        "start_date": "",
        "end_date": "",
        "details": ""
    }

    # Regex para capturar fechas estilo "Aug 2016 - Oct 2019" o "May 2014 - May 2016"
    date_pattern = re.compile(r"([A-Za-z]{3,}\s+\d{4})\s*-\s*([A-Za-z]{3,}\s+\d{4}|Present)", re.IGNORECASE)

    # Vamos recorriendo línea por línea
    for line in education_lines:
        # Si encontramos una línea que coincide con el patrón de fechas
        date_match = date_pattern.search(line)
        if date_match:
            # Si ya teníamos algo en current_block, lo agregamos a blocks
            if current_block["degree"] or current_block["institution"] or current_block["details"]:
                blocks.append(current_block)

            # Iniciamos un nuevo bloque
            current_block = {
                "degree": "",
                "institution": "",
                "start_date": date_match.group(1),
                "end_date": date_match.group(2),
                "details": ""
            }
        else:
            # Decidir si es 'degree', 'institution' o 'details'
            #  
            # - si current_block["degree"] está vacío => asumimos que es el grado
            # - si degree ya está y institution está vacío => es la institución
            # - si ya hay grado e institución => es parte de details
            if not current_block["degree"]:
                current_block["degree"] = line
            elif not current_block["institution"]:
                current_block["institution"] = line
            else:
                if current_block["details"]:
                    current_block["details"] += " " + line
                else:
                    current_block["details"] = line

    # Agregamos el último bloque si tiene info
    if current_block["degree"] or current_block["institution"] or current_block["details"]:
        blocks.append(current_block)

    return blocks


def extract_text_from_pdf(pdf_path):
    """Extrae y organiza la información del PDF en secciones."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    data = {
        "name": "",
        "job_title": "",
        "contact": "",
        "summary": "",
        "area_of_expertise": "",
        "key_achievements": "",
        "professional_experience": "",
        # EDUCATION será una lista de dicts
        "education": [],
        "additional_information": ""
    }

    # Detectar Nombre y Cargo (simplificado)
    if lines:
        data["name"] = lines[0]
        if len(lines) > 1 and lines[1].isupper():
            data["job_title"] = lines[1]

    # Buscar contacto (email)
    contact_regex = re.compile(r".+@.+\..+")
    for line in lines:
        if contact_regex.search(line):
            data["contact"] = line
            break

    sections_content = {}
    current_section = "summary"

    for line in lines:
        line_up = line.upper()
        if line_up in SECTION_TITLES:
            if line_up == "AREA OF EXPERTISE":
                current_section = "area_of_expertise"
            elif line_up == "KEY ACHIEVEMENTS":
                current_section = "key_achievements"
            elif line_up == "PROFESSIONAL EXPERIENCE":
                current_section = "professional_experience"
            elif line_up == "EDUCATION":
                current_section = "education"
            elif line_up == "ADDITIONAL INFORMATION":
                current_section = "additional_information"
        else:
            sections_content.setdefault(current_section, [])
            sections_content[current_section].append(line)

    # Convertimos secciones a string, excepto EDUCATION que parseamos
    for sec, lines_list in sections_content.items():
        if sec == "education":
            data["education"] = parse_education_block(lines_list)
        else:
            data[sec] = "\n".join(lines_list).strip()

    return data


def upload_resume(request):
    if request.method == "POST" and request.FILES.get("resume"):
        file = request.FILES["resume"]
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)

        # Extraemos los datos del PDF
        extracted_data = extract_text_from_pdf(fs.path(filename))

        # Guardamos en la BD
        resume = UploadedResume.objects.create(
            name=extracted_data.get("name", ""),
            job_title=extracted_data.get("job_title", ""),
            contact=extracted_data.get("contact", ""),
            summary=extracted_data.get("summary", ""),
            professional_experience=extracted_data.get("professional_experience", ""),
            education=extracted_data.get("education", "")
        )

        # Renderizamos la vista previa con el ID del CV guardado
        return render(request, "resume_preview.html", {
            "resume_data": extracted_data,
            "resume_id": resume.id  # Aseguramos que el ID esté disponible en la plantilla
        })

    return render(request, "upload.html")

def resume_list(request):
    resumes = UploadedResume.objects.all()
    return render(request, "resume_list.html", {"resumes": resumes})

def generate_pdf(request, resume_id):
    """Genera un PDF con toda la información correctamente estructurada."""

    # Obtener la hoja de vida desde la base de datos
    resume = UploadedResume.objects.get(id=resume_id)

    # Función para cargar JSON de forma segura (solo para education y experience)
    def safe_load_json(data):
        if isinstance(data, str) and data.strip():
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return []
        elif isinstance(data, list):
            return data
        return []

    # Convertir los datos de educación y experiencia a listas
    education_data = safe_load_json(resume.education)
    experience_data = safe_load_json(resume.professional_experience)

    # 🚀 Aquí NO debemos convertir a JSON: ya son cadenas de texto en la BD
    expertise_text = resume.expertise if resume.expertise else "SIN INFORMACIÓN"
    achievements_text = resume.achievements if resume.achievements else "SIN INFORMACIÓN"
    additional_info_text = resume.additional_info if resume.additional_info else "SIN INFORMACIÓN"

    # Depuración: Verificar qué datos estamos recuperando
    print("Datos extraídos:")
    print(f"Nombre: {resume.name}")
    print(f"Título de Trabajo: {resume.job_title}")
    print(f"Resumen: {resume.summary}")
    print(f"Área de experiencia: {expertise_text}")
    print(f"Logros clave: {achievements_text}")
    print(f"Experiencia profesional: {experience_data}")
    print(f"Educación: {education_data}")
    print(f"Información adicional: {additional_info_text}")

    # Crear el PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Configuración del formato
    line_height = 20
    x_offset = 50
    y_offset = height - 50  # Comenzar desde arriba

    def write_line(text, bold=False):
        """Escribe una línea en el PDF y baja el cursor"""
        nonlocal y_offset
        if bold:
            p.setFont("Helvetica-Bold", 12)
        else:
            p.setFont("Helvetica", 10)
        p.drawString(x_offset, y_offset, text)
        y_offset -= line_height

    # Función para evitar que los campos queden vacíos
    def safe_text(value):
        return str(value).strip() if value and str(value).strip() else "SIN INFORMACIÓN"

    # Escribir el contenido en el PDF
    write_line("NAME", bold=True)
    write_line(safe_text(resume.name))
    write_line("")
    
    write_line("JOB TITLE", bold=True)
    write_line(safe_text(resume.job_title))
    write_line("")
    
    write_line("CONTACT INFORMATION", bold=True)
    write_line(safe_text(resume.contact))
    write_line("")
    
    write_line("SUMMARY", bold=True)
    write_line(safe_text(resume.summary))
    write_line("")
    
    write_line("AREA OF EXPERTISE", bold=True)
    write_line(safe_text(expertise_text))
    write_line("")
    
    write_line("KEY ACHIEVEMENTS", bold=True)
    write_line(safe_text(achievements_text))
    write_line("")
    
    if education_data:
        write_line("EDUCATION", bold=True)
        for edu in education_data:
            write_line(safe_text(edu.get('degree')))
            write_line(safe_text(edu.get('institution')))
            write_line(f"{safe_text(edu.get('start_date'))} - {safe_text(edu.get('end_date'))}")
            if edu.get('details'):
                write_line(safe_text(edu['details']))
            write_line("-")
        write_line("")
    
    if experience_data:
        write_line("PROFESSIONAL EXPERIENCE", bold=True)
        for exp in experience_data:
            write_line(safe_text(exp.get('position')))
            write_line(safe_text(exp.get('company')))
            write_line(f"{safe_text(exp.get('start_date'))} - {safe_text(exp.get('end_date'))}")
            if exp.get('details'):
                write_line(safe_text(exp['details']))
            write_line("-")
        write_line("")
    
    write_line("ADDITIONAL INFORMATION", bold=True)
    write_line(safe_text(additional_info_text))
    write_line("")

    # Finalizar y guardar el PDF
    p.showPage()
    p.save()
    buffer.seek(0)

    # Generar nombre del archivo con el nombre de la persona y el cargo
    pdf_filename = f"Resume_{resume.name.replace(' ', '_')}_{resume.job_title.replace(' ', '_')}.pdf"

    # Preparar la respuesta HTTP con el PDF adjunto
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
    return response

def confirmation(request, resume_id):
    return render(request, "confirmation.html", {"resume_id": resume_id})

def resume_preview(request, resume_id):
    print(f"🔍 DEBUG: Recibido resume_id = {resume_id}")  # Depuración en consola
    
    resume = UploadedResume.objects.filter(id=resume_id).first()
    
    if not resume:
        print("⚠️ DEBUG: Hoja de vida no encontrada")
        return redirect("upload_resume")  # Redirige si no se encuentra el ID

    if request.method == "POST":
        print("📝 DEBUG: Guardando datos en la base de datos...")  # Depuración
        
        resume.name = request.POST.get("name", resume.name)
        resume.job_title = request.POST.get("job_title", resume.job_title)
        resume.contact = request.POST.get("contact", resume.contact)
        resume.summary = request.POST.get("summary", resume.summary)
        resume.professional_experience = request.POST.get("professional_experience", resume.professional_experience)
        resume.achievements = request.POST.get("achievements", resume.achievements)
        resume.expertise = request.POST.get("expertise", resume.expertise)
        resume.additional_info = request.POST.get("additional_info", resume.additional_info)

        # Guardamos educación en JSON
        education_list = []
        for i in range(1, 10):  
            degree = request.POST.get(f"degree_{i}", "").strip()
            institution = request.POST.get(f"institution_{i}", "").strip()
            start_date = request.POST.get(f"start_date_{i}", "").strip()
            end_date = request.POST.get(f"end_date_{i}", "").strip()
            details = request.POST.get(f"details_{i}", "").strip()

            if degree and institution:
                education_list.append({
                    "degree": degree,
                    "institution": institution,
                    "start_date": start_date,
                    "end_date": end_date,
                    "details": details
                })

        resume.education = json.dumps(education_list)  # Guardamos como JSON
        resume.save()

        print(f"✅ DEBUG: Hoja de vida {resume.id} guardada correctamente.")  # Depuración

        # 🔹 Redirigir a confirmation.html con el ID de la hoja de vida guardada
        return redirect(reverse("confirmation", kwargs={"resume_id": resume.id}))

    return render(request, "resume_preview.html", {"resume_data": resume, "resume_id": resume.id})

def confirm_and_save(request, resume_id):
    """Finaliza el proceso de guardado y redirige a la vista de confirmación."""
    
    # Obtener la hoja de vida guardada
    resume = UploadedResume.objects.get(id=resume_id)

    # Redirigir a la confirmación con el ID de la hoja de vida guardada
    return redirect(reverse("confirmation") + f"?resume_id={resume.id}")