from rest_framework import serializers

from .models import ICDModel


class ICDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICDModel
        fields = "__all__"
        read_only_fields = ["id"]
        # The model columns are nullable (the CSV has gaps), but a *new* record
        # must at least identify itself.
        extra_kwargs = {
            "category_code": {"required": True, "allow_blank": False, "allow_null": False},
            "full_code": {"required": True, "allow_blank": False, "allow_null": False},
            "full_description": {"required": True, "allow_blank": False, "allow_null": False},
        }

    def validate_full_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        duplicates = ICDModel.objects.filter(full_code__iexact=value)
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError("An ICD record with this full code already exists.")
        return value


class SearchQuerySerializer(serializers.Serializer):
    """Only used to describe the ``query`` parameter in the Swagger docs."""

    query = serializers.CharField(required=False, allow_blank=True)
