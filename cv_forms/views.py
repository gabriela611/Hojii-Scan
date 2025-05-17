from django.shortcuts import render, redirect, get_object_or_404
from .forms import PersonalInfoForm, EducationInfoForm,WorkExperience
from .models import PersonalInfo
from .forms import WorkExperienceFormSet
from .forms import HabilidadesCompetenciasForm
from .models import HabilidadesCompetencias
from .models import  PersonalInfo
from .models import EducationInfo
from django.http import HttpResponse
from .utils.json_bulilder import CvJsonBuilder
from .utils.pdf_generator import PdfGenerator
import json

def personal_info_view(request):
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST)
        if form.is_valid():
            personal_info = form.save()  # Guardamos el objeto en la BD
            request.session['personal_info_id'] = personal_info.id  # Guardamos el ID en la sesión
            return redirect('education_info')
    else:
        form = PersonalInfoForm()

    return render(request, 'personal_info.html', {'form': form})

def education_info_view(request):
    personal_info_id = request.session.get('personal_info_id')
    if not personal_info_id:
        return redirect('personal_info')  # Redirige si no hay ID en la sesión

    personal_info = PersonalInfo.objects.get(id=personal_info_id)

    if request.method == 'POST':
        print("📩 Datos recibidos en POST:", request.POST)  # Verificar datos recibidos

        # Guardar información de secundaria
        if request.POST.get('institucion_secundaria'):
            EducationInfo.objects.create(
                personal_info=personal_info,
                tipo='secundaria',
                institucion=request.POST.get('institucion_secundaria'),
                titulo=request.POST.get('titulo_secundaria'),
                fecha_inicio=request.POST.get('fecha_inicio_secundaria'),
                fecha_fin=request.POST.get('fecha_fin_secundaria')
            )

        # Guardar información universitaria
        if request.POST.get('institucion_universitaria'):
            EducationInfo.objects.create(
                personal_info=personal_info,
                tipo='universitaria',
                institucion=request.POST.get('institucion_universitaria'),
                titulo=request.POST.get('titulo_universitaria'),
                fecha_inicio=request.POST.get('fecha_inicio_universitaria'),
                fecha_fin=request.POST.get('fecha_fin_universitaria')
            )

        # Guardar información de posgrado
        if request.POST.get('institucion_posgrado'):
            EducationInfo.objects.create(
                personal_info=personal_info,
                tipo='posgrado',
                institucion=request.POST.get('institucion_posgrado'),
                titulo=request.POST.get('titulo_posgrado'),
                fecha_inicio=request.POST.get('fecha_inicio_posgrado'),
                fecha_fin=request.POST.get('fecha_fin_posgrado')
            )

        # Guardar información de otros estudios
        if request.POST.get('institucion_otros'):
            EducationInfo.objects.create(
                personal_info=personal_info,
                tipo='otros',
                institucion=request.POST.get('institucion_otros'),
                titulo=request.POST.get('titulo_otros'),
                fecha_inicio=request.POST.get('fecha_inicio_otros'),
                fecha_fin=request.POST.get('fecha_fin_otros')
            )

        print("✅ Redirigiendo a Work Experience")  # Depuración
        return redirect('work_experience', personal_id=personal_info.id)

    else:
        form = EducationInfoForm()

    return render(request, 'education_info.html', {'form': form, 'personal_info': personal_info})

def work_experience_view(request, personal_id):
    personal_info = PersonalInfo.objects.get(id=personal_id)

    if request.method == "POST":
        formset = WorkExperienceFormSet(request.POST, prefix='work_experience')
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.personal_info = personal_info  # Asignar la relación
                instance.save()
            return redirect('habilidades_competencias')
    else:
        formset = WorkExperienceFormSet(queryset=WorkExperience.objects.filter(personal_info=personal_info), prefix='work_experience')

    return render(request, 'work_experience.html', {'formset': formset, 'personal_info': personal_info})

def habilidades_competencias_view(request):
    # Verifica que el usuario tenga una sesión válida
    if not request.session.get('personal_info_id'):
        return redirect('pagina_de_inicio')
    
    try:
        personal_info = PersonalInfo.objects.get(id=request.session['personal_info_id'])
    except PersonalInfo.DoesNotExist:
        return redirect('pagina_de_inicio')

    # Obtiene o crea las habilidades
    habilidades, created = HabilidadesCompetencias.objects.get_or_create(
        personal_info=personal_info
    )

    if request.method == 'POST':
        print(f"📩 Datos recibidos en habilidades POST: {request.POST}")
        form = HabilidadesCompetenciasForm(request.POST, instance=habilidades)
        if form.is_valid():
            instancia = form.save()
            print("✅ Datos guardados:")
            print(f"Habilidades técnicas: {instancia.habilidades_tecnicas}")
            print(f"Cualidades personales: {instancia.cualidades_personales}")
            print(f"Idiomas: {instancia.idiomas}")
            print(f"Trabajo deseado: {instancia.trabajo_deseado}")
            
            return redirect('hoja_vida', documento=personal_info.documento)
        else:
            print("❌ Errores en el formulario:")
            print(form.errors)
    else:
        form = HabilidadesCompetenciasForm(instance=habilidades)

    return render(request, 'habilidades_competencias.html', {
        'form': form,
        'personal_info': personal_info
    })

def hoja_vida(request, documento):
    try:
        personal_info = PersonalInfo.objects.select_related('habilidades').get(documento=documento)
        
        print("=== Hoja de vida cargada ===")
        print(f"Nombre: {personal_info.nombre}")
        print(f"Habilidades Técnicas: {personal_info.habilidades.habilidades_tecnicas}")
        print(f"Cualidades personales: {personal_info.habilidades.cualidades_personales}")
        print(f"Idiomas: {personal_info.habilidades.idiomas}")
        print(f"Trabajo deseado: {personal_info.habilidades.trabajo_deseado}")

        return render(request, 'hoja_vida.html', {
            'personal_info': personal_info,
        })
    except PersonalInfo.DoesNotExist:
        raise Http404("No existe la hoja de vida solicitada")


def generar_pdf(request, documento):
    personal_info = get_object_or_404(PersonalInfo, documento=documento)
    
    # 1. Construir JSON y guardar archivo
    builder = CvJsonBuilder(personal_info)
    json_path = builder.save_to_file()

    # 2. Leer JSON para generar PDF
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 3. Generar PDF
    pdf = PdfGenerator(data).generate_pdf()

    # 4. Responder PDF al usuario
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="hoja_vida_{documento}.pdf"'
    return response