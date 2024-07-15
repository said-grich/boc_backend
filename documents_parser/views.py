from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import GitHubSearchSerializer
from .utils import GitHubUtils
import zipfile
import tempfile
import os
class GitHubSearchView(APIView):
    def post(self, request):
        serializer = GitHubSearchSerializer(data=request.data)
        if serializer.is_valid():
            github_url = serializer.validated_data.get('github_url')
            query = serializer.validated_data['query']
            zip_file = serializer.validated_data.get('zip_file')

            github_utils = GitHubUtils()
            temp_dir = None

            try:
                if github_url:
                    temp_dir = github_utils.clone_repo(github_url)
                elif zip_file:
                    temp_dir = tempfile.mkdtemp()
                    zip_path = os.path.join(temp_dir, zip_file.name)
                    with open(zip_path, 'wb') as f:
                        for chunk in zip_file.chunks():
                            f.write(chunk)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                else:
                    return Response({"error": "Either 'github_url' or 'file' must be provided."}, status=status.HTTP_400_BAD_REQUEST)

                text_data = github_utils.read_all_files(temp_dir)
                
                return Response({"results": text_data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            finally:
                github_utils.cleanup(temp_dir)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
