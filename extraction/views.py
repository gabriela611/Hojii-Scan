from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from .forms import ImageUploadForm
from .models import ExtractedResume
from PIL import Image
import requests
import os
from django.core.files.storage import default_storage
from django.conf import settings
import json
from .strategies import OCRSpaceStrategy

"""
Este módulo implementa las vistas principales de la aplicación de extracción de texto.
Utiliza el patrón Strategy para la extracción de texto, lo que permite:
1. Separar la lógica de extracción de texto del resto de la aplicación
2. Cambiar fácilmente entre diferentes servicios de OCR
3. Mantener el código organizado y fácil de mantener
"""

def extract_text_from_image(image):
    """
    Extrae texto de una imagen usando la estrategia OCRSpace.
    
    Args:
        image: Archivo de imagen a procesar
        
    Returns:
        str: Texto extraído de la imagen
    """
    strategy = OCRSpaceStrategy()
    return strategy.extract_text(image)

def upload_image(request):
    """
    Vista para subir una imagen y extraer su texto.
    
    Args:
        request: Objeto HttpRequest con los datos del formulario
        
    Returns:
        HttpResponse: Renderiza la página de extracción con el texto extraído
    """
    extracted_text = None

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            extracted_text = extract_text_from_image(image)
    else:
        form = ImageUploadForm()

    return render(request, "extraction.html", {"form": form, "extracted_text": extracted_text})

def generate_resume(request):
    """
    Vista para generar el JSON con el texto editado del CV.
    
    Args:
        request: Objeto HttpRequest con los datos del formulario
        
    Returns:
        HttpResponse: Redirige a la página de éxito o renderiza el formulario
    """
    if request.method == "POST":
        # Capturar los datos del formulario
        name = request.POST.get("name", "hoja_de_vida")
        profession = request.POST.get("profession", "Sin especificar")
        edited_text = request.POST.get("edited_text", "")

        # Crear un diccionario con los datos del CV
        resume_data = {
            "name": name,
            "profession": profession,
            "content": edited_text,
            "sections": parse_resume_sections(edited_text)
        }

        # Convertir a JSON
        json_data = json.dumps(resume_data, ensure_ascii=False, indent=2)

        # Definir la ruta de almacenamiento en la carpeta "extraction"
        extraction_folder = os.path.join(settings.MEDIA_ROOT, 'extraction')
        if not os.path.exists(extraction_folder):
            os.makedirs(extraction_folder)

        json_path = os.path.join(extraction_folder, f"{name}.json")

        # Guardar el archivo JSON en la carpeta extraction
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)

        # Guardar la referencia en la base de datos
        resume = ExtractedResume(
            name=name,
            profession=profession,
            pdf_file=f"extraction/{name}.json"  # Guardamos la referencia al JSON
        )
        resume.save()

        return redirect("success")

    return render(request, "extraction.html")

def parse_resume_sections(text):
    """
    Parsea el texto del CV y extrae las secciones principales.
    
    Args:
        text (str): Texto del CV a parsear
        
    Returns:
        dict: Diccionario con las secciones y su contenido
    """
    sections = {}
    current_section = None
    current_content = []

    # Lista de posibles secciones del CV en español e inglés
    possible_sections = [
        # Secciones en español
        "HOJA DE VIDA",
        "CONTACTO",
        "NOMBRES Y APELLIDOS",
        "E-MAIL",
        "TELEFONO",
        "DIRECCION",
        "FECHA DE NACIMIENTO",
        "DATOS PERSONALES",
        "PERFIL PROFESIONAL",
        "EDUCACION",
        "FORMACION ACADEMICA",
        "LICENCIAS Y MEMBRESIAS",
        "EXPERIENCIA PROFESIONAL",
        "HABILIDADES",
        "IDIOMAS",
        "REFERENCIAS",
        # Secciones en inglés
        "AREA OF EXPERTISE",
        "KEY ACHIEVEMENTS",
        "PROFESSIONAL EXPERIENCE",
        "EDUCATION",
        "ADDITIONAL INFORMATION"
    ]

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Verificar si la línea es un título de sección
        is_section = False
        for section in possible_sections:
            if section in line:
                # Si ya teníamos una sección anterior, guardarla
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = section
                current_content = []
                is_section = True
                break

        if not is_section and current_section:
            current_content.append(line)

    # Guardar la última sección
    if current_section:
        sections[current_section] = '\n'.join(current_content)

    return sections

# Vista principal para extracción
def extraction_view(request):
    extracted_text = None
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            extracted_text = extract_text_from_image(image)
    else:
        form = ImageUploadForm()

    return render(request, 'extraction.html', {'form': form, 'extracted_text': extracted_text})

def success_view(request):
    # Obtener el último JSON guardado en la base de datos
    last_resume = ExtractedResume.objects.last()
    if last_resume:
        # Leer el JSON
        json_path = os.path.join(settings.MEDIA_ROOT, last_resume.pdf_file.name)
        with open(json_path, 'r', encoding='utf-8') as json_file:
            resume_data = json.loads(json_file.read())

        # Crear un buffer para generar un nuevo PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Escribir el texto en el PDF
        c.setFont("Helvetica", 10)
        y_position = 750  # Posición inicial en el eje Y
        line_height = 15  # Altura entre líneas

        # Escribir el contenido del CV
        for line in resume_data['content'].splitlines():
            c.drawString(100, y_position, line[:100])  # Escribir cada línea (máximo 100 caracteres por línea)
            y_position -= line_height
            if y_position < 50:  # Si se alcanza el final de la página
                c.showPage()  # Crear una nueva página
                y_position = 750  # Reiniciar la posición Y

        c.save()
        buffer.seek(0)

        # Guardar el PDF en la carpeta temp
        temp_folder = os.path.join(settings.MEDIA_ROOT, 'temp')
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        pdf_path = os.path.join(temp_folder, f"{last_resume.name}.pdf")
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(buffer.getvalue())

        pdf_url = f"/media/temp/{last_resume.name}.pdf"
    else:
        pdf_url = None

    return render(request, "success.html", {"pdf_url": pdf_url})