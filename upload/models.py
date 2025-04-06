from django.db import models
from django.utils.timezone import now

# Create your models here.

class UploadedResume(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)  
    job_title = models.CharField(max_length=255, blank=True, null=True)  
    contact = models.TextField(blank=True, null=True)  
    summary = models.TextField(blank=True, null=True)  
    professional_experience = models.TextField(blank=True, null=True)  
    education = models.JSONField(blank=True, null=True, default=list)  
    achievements = models.TextField(blank=True, null=True)  
    expertise = models.TextField(blank=True, null=True)  
    additional_info = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(default=now, editable=False)  

    def __str__(self):
        return self.name if self.name else "Resume"