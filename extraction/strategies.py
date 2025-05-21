from abc import ABC, abstractmethod
import requests
from PIL import Image
import os
from django.conf import settings
from dotenv import load_dotenv

## Cargar variables de entorno desde .env,
load_dotenv()

class TextExtractionStrategy(ABC):
    """Clase base abstracta para las estrategias de extracción de texto"""
    
    @abstractmethod
    def extract_text(self, image):
        """Método abstracto para extraer texto de una imagen"""
        pass

class OCRSpaceStrategy(TextExtractionStrategy):
    """Estrategia que utiliza OCR.space API para extraer texto"""
    
    def __init__(self):
        self.api_key = os.environ.get('OCR_SPACE_API_KEY')
    
    def _prepare_image(self, image):
        """Prepara la imagen para el procesamiento"""
        image = Image.open(image)
        
        # Convertir la imagen a RGB si tiene canal alfa
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1])
            image = background
        
        return image
    
    def extract_text(self, image):
        """Extrae texto usando OCR.space API"""
        # Preparar la imagen
        image = self._prepare_image(image)
        
        # Guardar la imagen temporalmente
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_image.jpg')
        image.save(temp_path, 'JPEG', quality=95)
        
        # Configurar los parámetros para la API
        payload = {
            'apikey': self.api_key,
            'language': 'spa',
            'isOverlayRequired': 'true',
            'detectOrientation': 'true',
            'scale': 'true',
            'OCREngine': '2',
            'isTable': 'false',
            'filetype': 'jpg'
        }
        
        try:
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
                    text_overlay = text_result.get('TextOverlay', {})
                    lines = text_overlay.get('Lines', [])
                    
                    # Ordenar las líneas por posición Y
                    lines.sort(key=lambda x: x.get('MinTop', 0))
                    
                    current_y = None
                    for line in lines:
                        line_text = line.get('LineText', '').strip()
                        if not line_text:
                            continue
                        
                        line_y = line.get('MinTop', 0)
                        if current_y is not None and abs(line_y - current_y) > 20:
                            extracted_text += '\n'
                        
                        extracted_text += line_text + '\n'
                        current_y = line_y
                    
                    extracted_text += '\n'
                
                return extracted_text.strip()
            else:
                return "Error al conectar con el servicio OCR"
                
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return f"Error durante el procesamiento: {str(e)}"

class TesseractStrategy(TextExtractionStrategy):
    """Estrategia que utiliza Tesseract OCR para extraer texto"""
    
    def extract_text(self, image):
        """Extrae texto usando Tesseract OCR"""
        # Implementación futura si se necesita
        pass 