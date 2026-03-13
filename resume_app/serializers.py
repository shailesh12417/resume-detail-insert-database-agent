from rest_framework import serializers

class ResumeUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()