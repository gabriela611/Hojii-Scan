from django.shortcuts import render, redirect
from .forms import PersonalInfoForm, EducationInfoForm,WorkExperience
from .models import PersonalInfo
from .forms import WorkExperienceFormSet

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
        form = EducationInfoForm(request.POST)
        
        if form.is_valid():
            education_info = form.save(commit=False)
            education_info.personal_info = personal_info
            education_info.save()
            print("✅ Redirigiendo a Work Experience")  # Depuración
            return redirect('work_experience', personal_id=personal_info.id)

        else:
            print("❌ Error en el formulario:", form.errors.as_json())  # Ver errores detallados

    else:
        form = EducationInfoForm()

    return render(request, 'education_info.html', {'form': form, 'personal_info': personal_info})




def work_experience_view(request, personal_id):
    personal_info = PersonalInfo.objects.get(id=personal_id)
    
    if request.method == "POST":
        formset = WorkExperienceFormSet(request.POST, queryset=WorkExperience.objects.filter(personal_info=personal_info))
        
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.personal_info = personal_info  # Relacionar con la persona
                instance.save()
            return redirect('siguiente_pagina')  # Redirigir a la siguiente vista
    
    else:
        formset = WorkExperienceFormSet(queryset=WorkExperience.objects.filter(personal_info=personal_info))
    
    return render(request, 'work_experience.html', {'formset': formset, 'personal_info': personal_info})
