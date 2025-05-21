# 📝 Hojii-Scan  

Hojii-Scan es una aplicación web que permite extraer texto de imágenes de hojas de vida y convertirlo en un formato estructurado.

## 🚀 Instalación y Configuración  

### 1️⃣ Clonar el repositorio  

git clone https://github.com/tu_usuario/Hojii-Scan.git

cd Hojii-Scan

### 2️⃣ Crear y activar un entorno virtual

python -m venv env

source env/bin/activate  # Mac/Linux

env\Scripts\activate     # Window

### 3️⃣ Instalar dependencias

pip install -r requirements.txt

### 4️⃣ Configurar la base de datos

python manage.py migrate

### 5️⃣ Ejecutar el servidor

python manage.py runserver

## 📋 Características

- Extracción de texto de imágenes usando OCR.space API
- Procesamiento y estructuración del texto en secciones
- Generación de archivos JSON con la información extraída
- Interfaz web intuitiva y fácil de usar

## 📋 Requisitos

- Python 3.8 o superior
- Django 5.1 o superior
- Una cuenta en [OCR.space](https://ocr.space/ocrapi) para obtener una API key

## 📋 Uso

1. Abre tu navegador y ve a http://localhost:8000
2. Sube una imagen de una hoja de vida
3. El sistema extraerá el texto y lo mostrará en un formato editable
4. Edita el texto si es necesario
5. Guarda el resultado como JSON

## 📋 Estructura del Proyecto


Hojii-Scan/
├── extraction/          # Aplicación principal para extracción de texto
├── media/              # Archivos subidos y generados
│   ├── extraction/     # Archivos JSON
│   └── temp/          # Archivos temporales
├── templates/          # Plantillas HTML
└── manage.py          # Script de administración de Django


## 📋 Tecnologías Utilizadas

- Django: Framework web
- OCR.space API: Servicio de reconocimiento óptico de caracteres
- Bootstrap: Framework CSS para el diseño
- ReportLab: Generación de PDFs

## 📋 Contribuir

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (git checkout -b feature/AmazingFeature)
3. Commit tus cambios (git commit -m 'Add some AmazingFeature')
4. Push a la rama (git push origin feature/AmazingFeature)
5. Abre un Pull Request