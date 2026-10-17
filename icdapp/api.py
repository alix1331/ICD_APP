from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .serializers import ICDSerializer, SearchQuerySerializer
from .models import ICDModel


# Function Based View API
@api_view(["GET"])
def icd_list_view(request, format=None):
    # Add Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # 10 items per page

    queryset = ICDModel.objects.all()
    page_obj = paginator.paginate_queryset(queryset, request)
    serializer = ICDSerializer(page_obj, many=True)
    return Response(serializer.data)


# @api_view(["GET"])
# def icd_retrieve_view(request,pk=None):
#     # queryset = ICDModel.objects.all()
#     try:
#         icd = ICDModel.objects.get(id=pk)
#         serializer = ICDSerializer(icd)
#         return Response(serializer.data)
#     except ICDModel.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def icd_retrieve_view(request, pk=None):
    queryset = ICDModel.objects.all()
    icd = get_object_or_404(queryset, pk=pk)
    serializer = ICDSerializer(icd)
    return Response(serializer.data)


# @api_view(["GET"])
# def icd_search_view(request):
#     # Add Pagination
#     paginator = PageNumberPagination()
#     paginator.page_size = 10  # 10 items per page
#
#     category_code = request.query_params.get("category_code")
#     queryset = ICDModel.objects.all()
#     if category_code is not None:
#         queryset = ICDModel.objects.filter(category_code__icontains=category_code)
#     page_obj = paginator.paginate_queryset(queryset, request)
#     serializer = ICDSerializer(page_obj, many=True)
#     return Response(serializer.data)


@api_view(["GET"])
@swagger_auto_schema(query_serializer=SearchQuerySerializer())
def icd_search_view(request):
    # Add Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # 10 items per page

    query = request.query_params.get("query", default="")
    queryset = ICDModel.objects.filter(Q(category_code__icontains=query)
                                       | Q(category_title__icontains=query)
                                       | Q(full_description__icontains=query))
    page_obj = paginator.paginate_queryset(queryset, request)
    serializer = ICDSerializer(page_obj, many=True)
    return Response(serializer.data)


# Class Based View
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10000


class IcdCodeListAPIView(ListAPIView):
    queryset = ICDModel.objects.all()
    serializer_class = ICDSerializer
    pagination_class = LargeResultsSetPagination


class IcdCodeRetrieveAPIView(RetrieveAPIView):
    queryset = ICDModel.objects.all()
    serializer_class = ICDSerializer


class IcdSearchAPIView(APIView):
    @swagger_auto_schema(query_serializer=SearchQuerySerializer())
    def get(self, request, format=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10

        query = request.query_params.get("query", default="")
        queryset = ICDModel.objects.filter(Q(category_code__icontains=query)
                                           | Q(category_title__icontains=query)
                                           | Q(full_description__icontains=query))
        page_obj = paginator.paginate_queryset(queryset, request)
        serializer = ICDSerializer(page_obj, many=True)
        return Response(serializer.data)


class IcdCodeListAPIViewWithSearch(ListAPIView):
    queryset = ICDModel.objects.all()
    serializer_class = ICDSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get("query", default="")
        queryset = queryset.filter(Q(category_code__icontains=query)
                                   | Q(category_title__icontains=query)
                                   | Q(full_description__icontains=query))
        return queryset

    @swagger_auto_schema(query_serializer=SearchQuerySerializer())
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
