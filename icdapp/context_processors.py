from django.conf import settings


def icd_settings(request):
    """Make the ICD_PUBLIC_ADD switch available in every template."""
    return {"ICD_PUBLIC_ADD": settings.ICD_PUBLIC_ADD}
