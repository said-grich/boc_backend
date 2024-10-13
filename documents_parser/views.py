from datetime import datetime
import json
from django.http import HttpResponse
from django.shortcuts import render
import pytz
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from documents_parser.models import ExtractedData
from .serializers import SearchSerializer
from .services import calculate_summary_statistics, exportAsWord_using_Search_id, format_results_by_file, process_uploaded_file, save_results_to_db, append_dicts, serialize_formatted_results
import tempfile
import os
import shutil
import gc
from django.forms.models import model_to_dict

from .services import export_search_results_to_word

CustomUser = get_user_model()

class SearchView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_files = request.FILES.getlist('files')
            tag_names = serializer.validated_data.get('tag_names')
            print(f"======================={type(tag_names)} ,, ----{tag_names}")
            
            # tag_names = json.loads(tag_names)
            user = request.user 
            temp_dir = None
            
            results_by_tag_exact = {tag: [] for tag in tag_names}
            results_by_tag_partial = {tag: [] for tag in tag_names}

            try:
                temp_dir = tempfile.mkdtemp()  # Create a temporary directory
                print("-------------------------------------------->",uploaded_files)
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    
                    
                    with open(file_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)

                    # try:
                        file_type,results_exact, results_partial= process_uploaded_file(file_path, uploaded_file.name, tag_names, user)
                        results_by_tag_exact=append_dicts(results_exact, results_by_tag_exact)
                        results_by_tag_partial=append_dicts(results_partial, results_by_tag_partial)
                        
   


                    # except ValueError as e:
                    #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                

                search_id =save_results_to_db(results_by_tag_exact,results_by_tag_partial ,uploaded_file.name, file_type, user)
                
                
                word_document,user_name,datetime_string_file=exportAsWord_using_Search_id(search_id,user.username)
                # Create a response with the Word document as an attachment
                response = HttpResponse(word_document, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="search_result_{search_id}_{user_name}_{datetime_string_file}".docx'

                return response

            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                gc.collect()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class SearchView(APIView):
#     def post(self, request):
#         serializer = SearchSerializer(data=request.data)
#         if serializer.is_valid():
#             uploaded_files = request.FILES.getlist('files')
#             tag_names = serializer.validated_data.get('tag_names')
#             user = "Test_User"  # Replace with actual user when integrating auth
#             temp_dir = None
            
#             results_by_tag_exact = {tag: [] for tag in tag_names}
#             results_by_tag_partial = {tag: [] for tag in tag_names}

#             try:
#                 temp_dir = tempfile.mkdtemp()  # Create a temporary directory

#                 for uploaded_file in uploaded_files:
#                     file_path = os.path.join(temp_dir, uploaded_file.name)
                    
                    
#                     with open(file_path, 'wb') as f:
#                         for chunk in uploaded_file.chunks():
#                             f.write(chunk)

#                     # try:
#                         file_type,results_exact, results_partial= process_uploaded_file(file_path, uploaded_file.name, tag_names, user)
#                         results_by_tag_exact=append_dicts(results_exact, results_by_tag_exact)
#                         results_by_tag_partial=append_dicts(results_partial, results_by_tag_partial)
                        
   


#                     # except ValueError as e:
#                     #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                

#                 # Save results to DB
#                 search_id =save_results_to_db(results_by_tag_exact,results_by_tag_partial ,uploaded_file.name, file_type, user)
#                 search_results = format_results_by_file(search_id)
#                 serialized_formatted_results = serialize_formatted_results(search_results)
#                 summary_statistics = calculate_summary_statistics(serialized_formatted_results)
                
#                 return Response({"results":serialized_formatted_results,"summary":summary_statistics}, status=status.HTTP_200_OK)

#             finally:
#                 if temp_dir and os.path.exists(temp_dir):
#                     shutil.rmtree(temp_dir)
#                 gc.collect()

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExportSearchResultsView(APIView):
    def get(self, request, search_id):
        # try:
            # Retrieve the search results from the database using the search_id

            word_document,user_name,datetime_string_file=exportAsWord_using_Search_id(search_id)
            # Create a response with the Word document as an attachment
            response = HttpResponse(word_document, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="search_result_{search_id}_{user_name}_{datetime_string_file}".docx'

            return response

        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def search_page(request):
    return render(request, 'search-page.html')