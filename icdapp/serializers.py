from rest_framework import serializers
from .models import ICDModel


class ICDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICDModel
        fields = "__all__"


class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField()
