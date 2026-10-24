from django.db import models


# Columns mirror icd_codes.csv:
# ,category_code,diagnosis_code,full_code,abbreviated_description,full_description,category_title
class ICDModel(models.Model):
    # Indexes help exact / prefix lookups (e.g. the duplicate-code check when
    # adding a record). They do NOT speed up "contains" (icontains) searches.
    category_code = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    diagnosis_code = models.CharField(max_length=100, blank=True, null=True)
    full_code = models.CharField(max_length=500, blank=True, null=True, db_index=True)
    abbreviated_description = models.CharField(max_length=5000, blank=True, null=True)
    full_description = models.CharField(max_length=5000, blank=True, null=True)
    category_title = models.CharField(max_length=200, blank=True, null=True, db_index=True)

    class Meta:
        # A stable default order makes pagination deterministic.
        ordering = ["id"]
        verbose_name = "ICD code"
        verbose_name_plural = "ICD codes"

    def __str__(self):
        return self.full_code or self.category_code or f"ICD #{self.pk}"
