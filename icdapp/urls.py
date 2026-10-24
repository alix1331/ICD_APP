from django.conf import settings
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import api
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="ICD Codes API",
        default_version="v1",
        description=(
            "ICD Codes - Classification of Disease. "
            "Reading is public; creating and deleting records requires a staff account."
        ),
        contact=openapi.Contact(email=settings.API_CONTACT_EMAIL),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # Web UI
    path("", views.index_view, name="index"),
    path("about/", views.about_view, name="about"),
    path("icd/add/", views.add_view, name="icd_add"),
    path("icd/<int:pk>/delete/", views.delete_view, name="icd_delete"),

    # API documentation
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # API v1 - function based views
    # GET /api/v1/icd/list/  | POST (staff) creates a record
    path("api/v1/icd/list/", api.icd_list_view, name="icd_list"),
    # GET /api/v1/icd/code/<id>  | DELETE (staff) removes it
    path("api/v1/icd/code/<int:pk>", api.icd_retrieve_view, name="icd_retrieve"),
    # GET /api/v1/icd/search/?query=...
    path("api/v1/icd/search/", api.icd_search_view, name="icd_search"),

    # API v2 - class based views
    path("api/v2/icd/list/", api.IcdCodeListAPIView.as_view(), name="list_icd"),
    path("api/v2/icd/list-search/", api.IcdCodeListAPIViewWithSearch.as_view(), name="lists_icd"),
    path("api/v2/icd/code/<int:pk>", api.IcdCodeRetrieveAPIView.as_view(), name="retrieve_icd"),
    path("api/v2/icd/search/", api.IcdSearchAPIView.as_view(), name="search_icd"),
]
