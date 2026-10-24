from django.contrib import admin

from .models import ICDModel


@admin.register(ICDModel)
class ICDModelAdmin(admin.ModelAdmin):
    list_display = ("id", "full_code", "category_code", "category_title", "abbreviated_description")
    search_fields = ("full_code", "category_code", "category_title", "full_description")
    list_per_page = 50
    show_full_result_count = False  # avoids a slow COUNT(*) on a large table
