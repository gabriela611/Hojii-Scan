from django.contrib import admin
from .models import PersonalInfo, EducationInfo, WorkExperience

admin.site.register(PersonalInfo)
admin.site.register(EducationInfo)
admin.site.register(WorkExperience)