from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from .forms import ImageUploadForm
from .models import ExtractedResume
from PIL import Image
import pytesseract
from django.core.files.storage import default_storage
from django.conf import settings
import os

# Configura la ruta de Tesseract OCR si es necesario
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Función para extraer texto de la imagen
def extract_text_from_image(image):
    image = Image.open(image)  # Abrir la imagen
    text = pytesseract.image_to_string(image)  # OCR para extraer texto
    return text

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

# Vista para generar el PDF con el texto editado
def generate_pdf(request):
    if request.method == "POST":
        # Capturar los datos del formulario
        name = request.POST.get("name", "hoja_de_vida")
        profession = request.POST.get("profession", "Sin especificar")
        edited_text = request.POST.get("edited_text", "")

        # Crear un buffer para generar un nuevo PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Escribir el texto ingresado en el PDF
        c.setFont("Helvetica", 10)
        y_position = 750  # Posición inicial en el eje Y
        line_height = 15  # Altura entre líneas

        # Dividir el texto en líneas si es necesario
        for line in edited_text.splitlines():
            c.drawString(100, y_position, line[:100])  # Escribir cada línea (máximo 100 caracteres por línea)
            y_position -= line_height
            if y_position < 50:  # Si se alcanza el final de la página
                c.showPage()  # Crear una nueva página
                y_position = 750  # Reiniciar la posición Y

        c.save()
        buffer.seek(0)

        # Definir la ruta de almacenamiento en la carpeta "extraction"
        pdf_folder = os.path.join(settings.MEDIA_ROOT, 'extraction')
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)  # Crear la carpeta si no existe

        pdf_path = os.path.join(pdf_folder, f"{name}.pdf")

        # Guardar el archivo PDF en la carpeta especificada
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(buffer.getvalue())

        # Guardar la referencia en la base de datos
        resume = ExtractedResume(
            name=name,
            profession=profession,
            pdf_file=f"extraction/{name}.pdf"
        )
        resume.save()

        return redirect("success")  # Redirigir a una página de éxito

    return render(request, "extraction.html")

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
    # Obtener el último PDF guardado en la base de datos
    last_resume = ExtractedResume.objects.last()
    pdf_url = last_resume.pdf_file.url if last_resume else None

    return render(request, "success.html", {"pdf_url": pdf_url})