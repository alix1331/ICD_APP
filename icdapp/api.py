"""
REST API for ICD codes.

Reading (GET) is open to everyone. Creating (POST) and deleting (DELETE)
require a logged-in staff user, see ``icdapp.permissions.IsStaffOrReadOnly``.

Two flavours of the same API are provided:
    * v1: function-based views  (page size fixed at 10)
    * v2: class-based views     (page size configurable with ?page_size=)
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ICDModel
from .permissions import IsStaffOrReadOnly
from .serializers import ICDSerializer, SearchQuerySerializer


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
class StandardPagination(PageNumberPagination):
    """Fixed 10 items per page (used by the v1 function-based views)."""

    page_size = 10


class LargeResultsSetPagination(PageNumberPagination):
    """10 items per page by default, clients may ask for up to 10,000."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10000


def filter_by_query(queryset, query):
    """Case-insensitive substring search on category code, title and description."""
    query = (query or "").strip()
    if not query:
        return queryset
    return queryset.filter(
        Q(category_code__icontains=query)
        | Q(category_title__icontains=query)
        | Q(full_description__icontains=query)
    )


# --------------------------------------------------------------------------
# Function based views (v1)
# --------------------------------------------------------------------------
# Decorator order matters: swagger_auto_schema on top, then api_view, then
# permission_classes.
@swagger_auto_schema(
    method="post",
    request_body=ICDSerializer,
    responses={201: ICDSerializer, 400: "Validation error", 403: "Staff login required"},
)
@api_view(["GET", "POST"])
@permission_classes([IsStaffOrReadOnly])
def icd_list_view(request, format=None):
    """GET: paginated list of ICD records. POST (staff only): create a record."""
    if request.method == "POST":
        serializer = ICDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    paginator = StandardPagination()
    page = paginator.paginate_queryset(ICDModel.objects.all(), request)
    serializer = ICDSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@swagger_auto_schema(
    method="delete",
    responses={204: "Deleted", 403: "Staff login required", 404: "Not found"},
)
@api_view(["GET", "DELETE"])
@permission_classes([IsStaffOrReadOnly])
def icd_retrieve_view(request, pk=None, format=None):
    """GET: one ICD record by id. DELETE (staff only): remove it."""
    icd = get_object_or_404(ICDModel.objects.all(), pk=pk)
    if request.method == "DELETE":
        icd.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(ICDSerializer(icd).data)


@swagger_auto_schema(method="get", query_serializer=SearchQuerySerializer())
@api_view(["GET"])
def icd_search_view(request, format=None):
    """Search ICD records by category code, category title or full description."""
    query = request.query_params.get("query", "")
    queryset = filter_by_query(ICDModel.objects.all(), query)

    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = ICDSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


# --------------------------------------------------------------------------
# Class based views (v2)
# --------------------------------------------------------------------------
class IcdCodeListAPIView(ListCreateAPIView):
    """GET: paginated list. POST (staff only): create a record."""

    queryset = ICDModel.objects.all()
    serializer_class = ICDSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsStaffOrReadOnly]


class IcdCodeRetrieveAPIView(RetrieveDestroyAPIView):
    """GET: one record by id. DELETE (staff only): remove it."""

    queryset = ICDModel.objects.all()
    serializer_class = ICDSerializer
    permission_classes = [IsStaffOrReadOnly]


class IcdSearchAPIView(APIView):
    """Search by category code, category title or full description."""

    permission_classes = [IsStaffOrReadOnly]

    @swagger_auto_schema(query_serializer=SearchQuerySerializer(), responses={200: ICDSerializer(many=True)})
    def get(self, request, format=None):
        query = request.query_params.get("query", "")
        queryset = filter_by_query(ICDModel.objects.all(), query)

        paginator = LargeResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ICDSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class IcdCodeListAPIViewWithSearch(ListAPIView):
    """Paginated list that can optionally be narrowed with ?query=."""

    queryset = ICDModel.objects.all()
    serializer_class = ICDSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_by_query(queryset, self.request.query_params.get("query", ""))

    @swagger_auto_schema(query_serializer=SearchQuerySerializer())
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
