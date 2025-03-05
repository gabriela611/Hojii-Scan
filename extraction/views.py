from django.shortcuts import render

# Create your views here.
def extraction_view(request):
    return render(request, 'extraction.html')  # Archivo dentro de templates/