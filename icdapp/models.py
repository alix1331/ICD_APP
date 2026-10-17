from django.db import models


# Create your models here.
# ,category_code,diagnosis_code,full_code,abbreviated_description,full_description,category_title
class ICDModel(models.Model):
    category_code = models.CharField(max_length=50, blank=True, null=True)
    diagnosis_code = models.CharField(max_length=100, blank=True, null=True)
    full_code = models.CharField(max_length=500, blank=True, null=True)
    abbreviated_description = models.CharField(max_length=5000, blank=True, null=True)
    full_description = models.CharField(max_length=5000, blank=True, null=True)
    category_title = models.CharField(max_length=200, blank=True, null=True)
