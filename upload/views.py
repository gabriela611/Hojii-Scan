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
import os
from django.conf import settings
from difflib import get_close_matches

# Mapeo de encabezados posibles a las keys internas
SECTION_MAP = {
    # Inglés…
    "AREA OF EXPERTISE":       "area_of_expertise",
    "SKILLS":                  "area_of_expertise",
    "COMPETENCIES":            "area_of_expertise",
    # Español:
    "HABILIDADES":             "area_of_expertise",
    "COMPETENCIAS":            "area_of_expertise",
    #inglés
    "KEY ACHIEVEMENTS":        "key_achievements",
    "ACHIEVEMENTS":            "key_achievements",
    # Español:
    "LOGROS":                  "key_achievements",
    "LOGROS CLAVE":            "key_achievements",
    #inglés
    "PROFESSIONAL EXPERIENCE": "professional_experience",
    "WORK EXPERIENCE":         "professional_experience",
    # Español:
    "EXPERIENCIA PROFESIONAL": "professional_experience",
    "EXPERIENCIA LABORAL":     "professional_experience",
    #inglés
    "EDUCATION":               "education",
    # Español:
    "EDUCACIÓN":               "education",
    "FORMACIÓN ACADÉMICA":     "education",
    #inglés
    "ADDITIONAL INFORMATION":  "additional_information",
    # Español:
    "INFORMACIÓN ADICIONAL":   "additional_information",
    "INFORMACION ADICIONAL":   "additional_information",
}

def find_section(line):
    """Devuelve la sección interna más cercana a este encabezado."""
    line_up = line.upper()
    matches = get_close_matches(line_up, SECTION_MAP.keys(), n=1, cutoff=0.6)
    return SECTION_MAP[matches[0]] if matches else None

def parse_education_block(education_lines):
    blocks = []
    current_block = {
        "degree": "",
        "institution": "",
        "start_date": "",
        "end_date": "",
        "details": ""
    }
    date_pattern = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
    r"Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic)\s+\d{4})"
    r"\s*[-–]\s*"
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
    r"Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic|Present|Presente))",
    re.IGNORECASE
    )

    for line in education_lines:
        date_match = date_pattern.search(line)
        if date_match:
            if current_block["degree"] or current_block["institution"] or current_block["details"]:
                blocks.append(current_block)
            current_block = {
                "degree": "",
                "institution": "",
                "start_date": date_match.group(1),
                "end_date": date_match.group(2),
                "details": ""
            }
        else:
            if not current_block["degree"]:
                current_block["degree"] = line
            elif not current_block["institution"]:
                current_block["institution"] = line
            else:
                current_block["details"] += " " + line if current_block["details"] else line

    if current_block["degree"] or current_block["institution"] or current_block["details"]:
        blocks.append(current_block)

    return blocks


def extract_text_from_pdf(pdf_path):
    """Extrae y organiza la información del PDF en secciones (fuzzy-matching y heurístico en español)."""
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
        "education": [],
        "additional_information": ""
    }

    # — Heurístico ligero para nombre y cargo en español —
    if lines:
        # Nombre = primera línea
        data["name"] = lines[0]
        # Cargo = si la segunda línea está en mayúsculas completas, la toma;
        # si no, busca en las primeras 4 líneas alguna palabra clave de puesto.
        if len(lines) > 1 and lines[1].isupper():
            data["job_title"] = lines[1]
        else:
            for l in lines[1:5]:
                if any(k in l.lower() for k in ["ingeniero", "gerente", "analista", "diseñador", "desarrollador", "consultor"]):
                    data["job_title"] = l
                    break

    # Extraer contacto (email)
    contact_regex = re.compile(r".+@.+\..+")
    for line in lines:
        if contact_regex.search(line):
            data["contact"] = line
            break

    # Recorrer líneas con fuzzy-matching de secciones
    sections_content = {}
    current_section = "summary"
    for line in lines:
        sec = find_section(line)
        if sec:
            current_section = sec
        else:
            sections_content.setdefault(current_section, []).append(line)

    # Convertir contenido a data
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
        extracted_data = extract_text_from_pdf(fs.path(filename))

        resume = UploadedResume.objects.create(
            name=extracted_data.get("name", ""),
            job_title=extracted_data.get("job_title", ""),
            contact=extracted_data.get("contact", ""),
            summary=extracted_data.get("summary", ""),
            professional_experience=extracted_data.get("professional_experience", ""),
            education=extracted_data.get("education", "")
        )

        return render(request, "resume_preview.html", {
            "resume_data": extracted_data,
            "resume_id": resume.id
        })

    return render(request, "upload.html")


def resume_preview(request, resume_id):
    resume = UploadedResume.objects.filter(id=resume_id).first()
    if not resume:
        return redirect("upload_resume")

    if request.method == "POST":
        resume.name = request.POST.get("name", resume.name)
        resume.job_title = request.POST.get("job_title", resume.job_title)
        resume.contact = request.POST.get("contact", resume.contact)
        resume.summary = request.POST.get("summary", resume.summary)
        resume.professional_experience = request.POST.get(
            "professional_experience",
            resume.professional_experience
        )
        resume.achievements = request.POST.get(
            "key_achievements",
            resume.achievements
        )
        resume.expertise = request.POST.get(
            "area_of_expertise",
            resume.expertise
        )
        resume.additional_info = request.POST.get(
            "additional_information",
            resume.additional_info
        )

        # Construir lista de educación fija
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

        # Capturar bloques de educación dinámicos
        for key in request.POST.keys():
            if key.startswith("degree_new_"):
                suffix = key.replace("degree_new_", "")
                degree = request.POST.get(f"degree_new_{suffix}", "").strip()
                institution = request.POST.get(f"institution_new_{suffix}", "").strip()
                start_date = request.POST.get(f"start_date_new_{suffix}", "").strip()
                end_date = request.POST.get(f"end_date_new_{suffix}", "").strip()
                details = request.POST.get(f"details_new_{suffix}", "").strip()
                if degree and institution:
                    education_list.append({
                        "degree": degree,
                        "institution": institution,
                        "start_date": start_date,
                        "end_date": end_date,
                        "details": details
                    })

        # Guardar en la base de datos
        resume.education = json.dumps(education_list)
        resume.save()

        # —————— Guardar JSON en disco ——————
        resume_dict = {
            "id": resume.id,
            "name": resume.name,
            "job_title": resume.job_title,
            "contact": resume.contact,
            "summary": resume.summary,
            "professional_experience": resume.professional_experience,
            "achievements": resume.achievements,
            "expertise": resume.expertise,
            "additional_info": resume.additional_info,
            "education": json.loads(resume.education)
        }

        json_dir = os.path.join(settings.MEDIA_ROOT, "cv_json")
        os.makedirs(json_dir, exist_ok=True)

        json_path = os.path.join(json_dir, f"resume_{resume.id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(resume_dict, f, ensure_ascii=False, indent=4)

        return redirect(reverse("confirmation", kwargs={"resume_id": resume.id}))

    return render(
        request,
        "resume_preview.html",
        {"resume_data": resume, "resume_id": resume.id}
    )

def resume_list(request):
    resumes = UploadedResume.objects.all()
    return render(request, "resume_list.html", {"resumes": resumes})


def confirmation(request, resume_id):
    return render(request, "confirmation.html", {"resume_id": resume_id})


def generate_pdf(request, resume_id):
    resume = UploadedResume.objects.get(id=resume_id)

    def safe_load_json(data):
        if isinstance(data, str) and data.strip():
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return []
        elif isinstance(data, list):
            return data
        return []

    education_data = safe_load_json(resume.education)
    experience_data = safe_load_json(resume.professional_experience)
    expertise_text = resume.expertise or "SIN INFORMACIÓN"
    achievements_text = resume.achievements or "SIN INFORMACIÓN"
    additional_info_text = resume.additional_info or "SIN INFORMACIÓN"

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    line_height = 20
    x_offset = 50
    y_offset = height - 50

    def write_line(text, bold=False):
        nonlocal y_offset
        p.setFont("Helvetica-Bold" if bold else "Helvetica", 12 if bold else 10)
        p.drawString(x_offset, y_offset, text)
        y_offset -= line_height

    def safe_text(value):
        return str(value).strip() if value and str(value).strip() else "SIN INFORMACIÓN"

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

    write_line("ADDITIONAL INFORMATION", bold=True)
    write_line(safe_text(additional_info_text))
    write_line("")

    p.showPage()
    p.save()
    buffer.seek(0)

    pdf_filename = f"Resume_{resume.name.replace(' ', '_')}_{resume.job_title.replace(' ', '_')}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
    return response
