import pytesseract
from PIL import Image

def extract_text_from_image(image):
    image = Image.open(image)  # Abre la imagen
    text = pytesseract.image_to_string(image)  # Extrae el texto usando OCR
    return text