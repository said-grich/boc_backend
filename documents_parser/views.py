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

 
class SearchView(APIView):
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_files = request.FILES.getlist('files')
            tag_names = serializer.validated_data.get('tag_names')  # Assume 'tag_names' is a list of tags
            print(f"Tags ====>{tag_names}")
            temp_dir = None
            results_by_tag = {tag: [] for tag in tag_names}  # Initialize a dictionary to hold results by tag

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
                        # Use GitHubUtils for handling .zip files
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        text_data = read_all_files_in_directory(temp_dir)
                        
                    elif uploaded_file.name.endswith('.pdf'):
                        file_type = "PDF"
                        start_time = time.time()  # Record the start time

                        text_data = self.extract_text_from_pdf(file_path)  # Process PDF

                        end_time = time.time()  # Record the end time
                        elapsed_time = end_time - start_time
                        print(f"Time ------------{elapsed_time}")
                    elif uploaded_file.name.endswith('.docx'):
                        file_type = "WORD"
                        text_data = self.extract_text_from_docx(file_path)
                    elif uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.xlsx'):
                        file_type = "EXCEL"
                        text_data = self.extract_text_from_excel(file_path)
                    else:
                        return Response({"error": f"Unsupported file format: {uploaded_file.name}"}, status=status.HTTP_400_BAD_REQUEST)
                    if file_type =="Github":
                        for tag_name in tag_names:
                            for text in text_data:
                                results_for_tag = search_and_extract(text, tag_name, file_type, uploaded_file.name)
                                results_by_tag[tag_name].extend(results_for_tag)
                        
                    else:
                        for tag_name in tag_names:
                            results_for_tag = search_and_extract(text_data, tag_name, file_type, uploaded_file.name)
                            results_by_tag[tag_name].extend(results_for_tag)  # Append results to the corresponding tag's list
                        
                    # Clear the text data to free up memory
                    del text_data
                    import gc
                    gc.collect()  # Force garbage collection after each file

                return Response({"results": results_by_tag}, status=status.HTTP_200_OK)
            # except Exception as e:
            #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)  # Ensure the temporary directory is cleaned up
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def extract_text_from_pdf(self, pdf_path):
        # Ensure semaphore initialization and processing is done correctly
        init_semaphore(max_workers=2)  # Initialize semaphore
        text_data = extract_text_with_ocr(
            pdf_path,
            header_height=50,
            resolution=200,
            enhance_contrast=True,
            sharpen_image=False,
            use_parallel=True,
            max_workers=1
        )
        
        return clean_text(text_data)

    def extract_text_from_docx(self, docx_path):
        doc = docx.Document(docx_path)
        text_data= " ".join([para.text for para in doc.paragraphs])
        return clean_text(text_data)
 
    def extract_text_from_excel(self, excel_path):
        text_data = []
        if excel_path.endswith('.xls'):
            workbook = xlrd.open_workbook(excel_path)
            for sheet in workbook.sheets():
                for row_idx in range(sheet.nrows):
                    row = sheet.row(row_idx)
                    text_data.append(", ".join([str(cell.value) for cell in row]))
        elif excel_path.endswith('.xlsx'):
            workbook = openpyxl.load_workbook(excel_path)
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                for row in sheet.iter_rows(values_only=True):
                    text_data.append(", ".join([str(cell) for cell in row if cell is not None]))
        
        # Join the list of strings into a single string
        combined_text = " ".join(text_data)
        
        # Clean the combined text
        return clean_text(combined_text)

