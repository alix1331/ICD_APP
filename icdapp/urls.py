from django.urls import path
from . import views
from . import api
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="ICD Codes API",
      default_version='v1',
      description="ICD Codes - Classification of Disease",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@jcharistech.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path("", views.index_view,name="index"),
    path("about/", views.about_view,name="about"),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # API
    # /api/v1/icd/list/
    path("api/v1/icd/list/",api.icd_list_view,name="icd_list"),
    # /api/v1/icd/code/<id>
    path("api/v1/icd/code/<pk>",api.icd_retrieve_view,name="icd_retrieve"),
    # /api/v1/icd/search/
    path("api/v1/icd/search/", api.icd_search_view, name="icd_search"),

    # CBV
    path("api/v2/icd/list/", api.IcdCodeListAPIView.as_view(),name="list_icd"),
    path("api/v2/icd/code/<pk>",api.IcdCodeRetrieveAPIView.as_view(),name="retrieve_icd"),
    path("api/v2/icd/search/", api.IcdSearchAPIView.as_view(), name="search_icd"),
    path("api/v2/icd/list/", api.IcdCodeListAPIViewWithSearch.as_view(),name="lists_icd"),

]