from django.shortcuts import render, redirect
from .forms import PersonalInfoForm, EducationInfoForm
from .models import PersonalInfo

def personal_info_view(request):
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST)
        if form.is_valid():
            request.session['personal_info'] = form.cleaned_data  # Guardar en sesión
            return redirect('education_info')  # Ir a la siguiente página
    else:
        form = PersonalInfoForm()

    return render(request, 'personal_info.html', {'form': form})

def education_info_view(request):
    if request.method == 'POST':
        form = EducationInfoForm(request.POST)
        if form.is_valid():
            personal_info_data = request.session.get('personal_info')
            if personal_info_data:
                personal_info, created = PersonalInfo.objects.get_or_create(
                    documento=personal_info_data['documento'], defaults=personal_info_data
                )
                education_info = form.save(commit=False)
                education_info.personal_info = personal_info
                education_info.save()
                return redirect('personal_info')  # Puedes cambiar esto por una vista de resumen
    else:
        form = EducationInfoForm()

    return render(request, 'education_info.html', {'form': form})