from django.shortcuts import render, redirect
import pytesseract
from PIL import Image
from django.core.files.storage import default_storage
from io import BytesIO
from .forms import ImageUploadForm
from .models import ExtractedResume
from django.core.files.base import ContentFile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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
            image = request.FILES["image"]
            temp_path = default_storage.save("temp/" + image.name, image)
            text = extract_text_from_image(default_storage.path(temp_path))
            extracted_text = text  # Guardamos el texto extraído
            default_storage.delete(temp_path)  # Elimina el archivo temporal
    else:
        form = ImageUploadForm()

    return render(request, "extraction.html", {"form": form, "extracted_text": extracted_text})

# Vista para generar el PDF con el formato base
def generate_pdf(request):
    if request.method == "POST":
        name = request.POST.get("name", "hoja_de_vida")
        edited_text = request.POST.get("edited_text", "")

       # Construir la ruta al archivo PDF base
        template_path = settings.BASE_DIR / 'extraction' / 'static' / 'extraction' / 'Documento base de hoja de vida.pdf'
        if not template_path.exists():
            return render(request, "extraction.html", {"error": "El archivo base no se encontró."})

        with open(template_path, "rb") as f:
            reader = PdfReader(f)
            writer = PdfWriter()

            # Crear un nuevo PDF con el texto modificado
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)

            # Dibujar la primera página del PDF original
            page = reader.pages[0]
            writer.add_page(page)

            # Escribir el texto extraído en el formato base
            c.setFont("Helvetica", 10)
            c.drawString(100, 700, edited_text[:500])  # Ajusta la posición y tamaño del texto

            c.showPage()
            c.save()

            # Agregar el contenido modificado al PDF
            buffer.seek(0)
            writer.add_page(PdfReader(buffer).pages[0])

            # Guardar el nuevo PDF
            output_pdf = BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)

        # Guardamos el PDF en la base de datos
        pdf_file = ContentFile(output_pdf.getvalue(), name + ".pdf")
        resume = ExtractedResume(name=name, pdf_file=pdf_file)
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
    return render(request, "success.html", {"message": "El PDF se generó correctamente."})