from rest_framework import serializers

class GitHubSearchSerializer(serializers.Serializer):
    github_url = serializers.URLField(label='GitHub Repository URL', required=False)
    query = serializers.CharField(label='Search Query', required=True)
    zip_file = serializers.FileField(label='Upload ZIP File', required=False)
