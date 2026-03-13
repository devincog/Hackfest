from rest_framework import serializers


class UploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
    )


class GenerateSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    project_id = serializers.UUIDField(required=True)


class UpdateSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    project_id = serializers.UUIDField(required=True)
