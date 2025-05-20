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

# Función para extraer texto de la imagen usando OCR.space API
def extract_text_from_image(image):
    # Configurar la API key
    api_key = os.environ.get('OCR_SPACE_API_KEY')
    
    # Preparar la imagen para la API
    image = Image.open(image)
    
    # Convertir la imagen a RGB si tiene canal alfa
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1])  # Usar el canal alfa como máscara
        image = background
    
    # Guardar la imagen temporalmente
    temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_image.jpg')
    image.save(temp_path, 'JPEG', quality=95)
    
    # Configurar los parámetros para la API
    payload = {
        'apikey': api_key,
        'language': 'spa',  # Español
        'isOverlayRequired': 'true',  # Necesitamos las coordenadas para preservar el formato
        'detectOrientation': 'true',
        'scale': 'true',
        'OCREngine': '2',  # Motor OCR más preciso
        'isTable': 'false',
        'filetype': 'jpg'
    }
    
    # Enviar la imagen a la API
    with open(temp_path, 'rb') as f:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'file': f},
            data=payload
        )
    
    # Eliminar el archivo temporal
    os.remove(temp_path)
    
    # Procesar la respuesta
    if response.status_code == 200:
        result = response.json()
        if result['IsErroredOnProcessing']:
            return "Error al procesar la imagen"
        
        # Extraer el texto de la respuesta
        extracted_text = ''
        for text_result in result['ParsedResults']:
            # Obtener el texto con las coordenadas
            text_overlay = text_result.get('TextOverlay', {})
            lines = text_overlay.get('Lines', [])
            
            # Ordenar las líneas por posición Y (de arriba a abajo)
            lines.sort(key=lambda x: x.get('MinTop', 0))
            
            current_y = None
            for line in lines:
                line_text = line.get('LineText', '').strip()
                if not line_text:
                    continue
                
                # Obtener la posición Y de la línea actual
                line_y = line.get('MinTop', 0)
                
                # Si hay un cambio significativo en Y, agregar un salto de línea extra
                if current_y is not None and abs(line_y - current_y) > 20:  # Umbral de 20 píxeles
                    extracted_text += '\n'
                
                # Agregar el texto de la línea
                extracted_text += line_text + '\n'
                current_y = line_y
            
            # Agregar un salto de línea extra entre párrafos
            extracted_text += '\n'
        
        return extracted_text.strip()
    else:
        return "Error al conectar con el servicio OCR"

# Vista para subir imagen y extraer texto
def upload_image(request):
    extracted_text = None  # Variable para almacenar el texto extraído

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            extracted_text = extract_text_from_image(image)  # Extraer texto de la imagen
    else:
        form = ImageUploadForm()

    return render(request, "extraction.html", {"form": form, "extracted_text": extracted_text})

# Vista para generar el JSON con el texto editado
def generate_resume(request):
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
            os.makedirs(extraction_folder)  # Crear la carpeta si no existe

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

        return redirect("success")  # Redirigir a una página de éxito

    return render(request, "extraction.html")

def parse_resume_sections(text):
    """
    Función para parsear el texto del CV y extraer las secciones principales
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
        "LICENCIAS Y MEMBRESIAS"
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