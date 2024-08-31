from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SearchSerializer
import zipfile
import tempfile
import os
import PyPDF2  
import docx    
import xlrd   
import openpyxl
from .utils import *
from .models import *
import shutil
import time
import chardet
from .github_controller import *
import re
import gc
 
class SearchView(APIView):
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_files = request.FILES.getlist('files')
            tag_names = serializer.validated_data.get('tag_names')
              
            temp_dir = None
            text_data=None
            data_dict=None
            
            results_by_tag_exact = {tag: [] for tag in tag_names}
            results_by_tag_partial = {tag: [] for tag in tag_names}
            try:
                temp_dir = tempfile.mkdtemp()  # Create a temporary directory

                for uploaded_file in uploaded_files:
                    print(f"{uploaded_file}")
                    file_type = None
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)
                    
                    # Determine the file type and process accordingly
                    if uploaded_file.name.endswith('.zip'):
                        file_type = "Github"
                        zip_file_name=uploaded_file.name.split(".")[0]
                        # Use GitHubUtils for handling .zip files
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        data_dict = read_all_files_in_directory(temp_dir)
                        
                        for tag in tag_names:
                            result_exact,result_partial= search_github(tag,zip_file_name,data_dict)
                            results_by_tag_exact[tag]+=result_exact
                            results_by_tag_partial[tag]+=result_partial
                    
                    elif uploaded_file.name.endswith('.pdf'):
                        file_type = "PDF"
                        start_time = time.time()  # Record the start time
                        for tag in tag_names:
                            result_exact, result_partial=read_pdf_file(file_path,tag,uploaded_file.name,user="Test_User")
                            results_by_tag_exact[tag]+=result_exact
                            results_by_tag_partial[tag]+=result_partial
                        end_time = time.time()  
                        elapsed_time = end_time - start_time
                        print(f"Time ------------{elapsed_time}")
                        
                    elif uploaded_file.name.endswith('.docx'):
                        file_type = "Word"
                        
                        for tag in tag_names:
                            result_exact,result_partial= search_doc(file_path,tag,uploaded_file.name,user="Test_User")
                            results_by_tag_exact[tag]+=result_exact
                            results_by_tag_partial[tag]+=result_partial
                            
                    elif uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.xlsx'):
                        file_type = "EXCEL"
                        for tag in tag_names:
                            result_exact,result_partial= extract_text_from_excel(file_path,tag,uploaded_file.name,user="Test_User")
                            results_by_tag_exact[tag]+=result_exact
                            results_by_tag_partial[tag]+=result_partial
                    else:
                        return Response({"error": f"Unsupported file format: {uploaded_file.name}"}, status=status.HTTP_400_BAD_REQUEST)
                    
            

                return Response({"results_exact": results_by_tag_exact ,"results_partial": results_by_tag_partial }, status=status.HTTP_200_OK)

            finally:
                
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                gc.collect()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







