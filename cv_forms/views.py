from django.shortcuts import render, redirect
from .forms import PersonalInfoForm, EducationInfoForm
from .models import PersonalInfo

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
        form = EducationInfoForm(request.POST)
        if form.is_valid():
            education_info = form.save(commit=False)
            education_info.personal_info = personal_info  # Asignar relación
            education_info.save()
            return redirect('next_page')  # Redirigir a la siguiente sección
    else:
        form = EducationInfoForm()

    return render(request, 'education_info.html', {'form': form})
