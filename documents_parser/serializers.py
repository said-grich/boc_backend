from rest_framework import serializers

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
    tag_name = serializers.CharField(
        max_length=100,
        help_text="Tag name to search within the uploaded files"
    )

    def validate_files(self, value):
        # Add any additional validation for the files here if needed
        if not value:
            raise serializers.ValidationError("At least one file must be provided.")
        return value
