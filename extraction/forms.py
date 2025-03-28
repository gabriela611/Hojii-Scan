from django import forms
#Este formulario permitirá subir una imagen .png o .jpg.
class ImageUploadForm(forms.Form):
    image = forms.ImageField()
