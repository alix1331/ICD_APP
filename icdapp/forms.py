from django import forms

from .models import ICDModel


class ICDForm(forms.ModelForm):
    """Form used by the web UI to add a new ICD record."""

    class Meta:
        model = ICDModel
        fields = [
            "category_code",
            "diagnosis_code",
            "full_code",
            "abbreviated_description",
            "full_description",
            "category_title",
        ]
        widgets = {
            "category_code": forms.TextInput(attrs={"class": "form-control"}),
            "diagnosis_code": forms.TextInput(attrs={"class": "form-control"}),
            "full_code": forms.TextInput(attrs={"class": "form-control"}),
            "abbreviated_description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "full_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category_title": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Same minimum as the API: a record needs a category code, full code and description.
        for name in ("category_code", "full_code", "full_description"):
            self.fields[name].required = True

    def clean_full_code(self):
        value = (self.cleaned_data.get("full_code") or "").strip()
        duplicates = ICDModel.objects.filter(full_code__iexact=value)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("An ICD record with this full code already exists.")
        return value
