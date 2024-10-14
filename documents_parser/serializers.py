from rest_framework import serializers
from .models import ExtractedData

class GitHubSearchSerializer(serializers.Serializer):
    github_url = serializers.URLField(label='GitHub Repository URL', required=False)
    query = serializers.CharField(label='Search Query', required=True)
    zip_file = serializers.FileField(label='Upload ZIP File', required=False)


class SearchSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        help_text="List of files to be uploaded and processed"
    )
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )

    def validate_files(self, value):
        if not value:
            raise serializers.ValidationError("At least one file must be provided.")
        return value



class ExtractedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedData
        fields = '__all__'
