

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from documents_parser.models import ExtractedData
from .serializers import SearchSerializer
from .services import process_uploaded_file, save_results_to_db, append_dicts
import tempfile
import os
import shutil
import gc
from django.forms.models import model_to_dict

from .services import export_search_results_to_word

class SearchView(APIView):
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_files = request.FILES.getlist('files')
            tag_names = serializer.validated_data.get('tag_names')
            user = "Test_User"  # Replace with actual user when integrating auth
            temp_dir = None
            
            results_by_tag_exact = {tag: [] for tag in tag_names}
            results_by_tag_partial = {tag: [] for tag in tag_names}

            try:
                temp_dir = tempfile.mkdtemp()  # Create a temporary directory

                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    
                    with open(file_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)

                    try:
                        file_type,results_exact, results_partial= process_uploaded_file(file_path, uploaded_file.name, tag_names, user)
                        results_by_tag_exact=append_dicts(results_exact, results_by_tag_exact)
                        results_by_tag_partial=append_dicts(results_partial, results_by_tag_partial)
                        
   


                    except ValueError as e:
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                

                # Save results to DB
                saved_exact_results ,saved_partial_results =save_results_to_db(results_by_tag_exact,results_by_tag_partial ,uploaded_file.name, file_type, user)
                
                serialized_exact_results = [
                    {**model_to_dict(result), 'search_id': str(result.search_id)} for result in saved_exact_results
                ]
                serialized_partial_results = [
                    {**model_to_dict(result), 'search_id': str(result.search_id)} for result in saved_partial_results
                ]

                return Response({"results_exact": serialized_exact_results, "results_partial": serialized_partial_results}, status=status.HTTP_200_OK)

            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                gc.collect()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExportSearchResultsView(APIView):
    def get(self, request, search_id):
        # try:
            # Retrieve the search results from the database using the search_id
            search_results = ExtractedData.objects.filter(search_id=search_id)
            
            if not search_results.exists():
                return Response({"error": "No results found for the provided search_id."}, status=status.HTTP_404_NOT_FOUND)

            # Extract relevant information for filename
            source_file_name = search_results.first().source_file_name.split(".")[0]
            date_of_search = search_results.first().date_of_search.strftime("%Y-%m-%d")  # Format the date
            search_author = search_results.first().search_author

            # Prepare the filename using the format: search_result_<name_of_file>_<date_of_search>_<username>.docx
            filename = f"search_result_{source_file_name}_{date_of_search}_{search_author}.docx"

            # Generate the Word document from the search results
            word_document = export_search_results_to_word(search_results, source_file_name)

            # Create a response with the Word document as an attachment
            response = HttpResponse(word_document, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)