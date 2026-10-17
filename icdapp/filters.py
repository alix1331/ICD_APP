import django_filters
from django import forms
from .models import ICDModel


class ICDSearchFilter(django_filters.FilterSet):
    category_title = django_filters.CharFilter(lookup_expr="icontains",widget=forms.TextInput(attrs={"class":"form-control"}))
    category_code = django_filters.CharFilter(lookup_expr="icontains",
                                               widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = ICDModel
        fields = ['category_title', 'category_code']
