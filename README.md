# 📝 Hojii-Scan  

Hojii-Scan es una aplicación web desarrollada en **Django** que permite digitalizar hojas de vida. Ofrece funcionalidades para:  

✅ Subir archivos PDF y extraer información.  
✅ Tomar fotos de hojas de vida y procesarlas.  
✅ Llenar un formulario y generar una hoja de vida en una plantilla genérica.  

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
