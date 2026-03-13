from django.db import models

class Resume(models.Model):

    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    github = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)

    skills = models.TextField(null=True, blank=True)
    experience = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)