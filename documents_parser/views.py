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

 
class SearchView(APIView):
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_files = request.FILES.getlist('files')
            tag_name = serializer.validated_data.get('tag_name')
            print(f"Tag ====>{tag_name}")
            temp_dir = None
            result = []  # List to hold text data from all files

            try:
                temp_dir = tempfile.mkdtemp()  # Create a temporary directory

                for uploaded_file in uploaded_files:
                    file_type = None
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)
                    
                    # Determine the file type and process accordingly
                    if uploaded_file.name.endswith('.zip'):
                        file_type = "Github"
                        # Use GitHubUtils for handling .zip files
                        github_utils = GitHubUtils()
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        text_data = self.read_all_files_in_directory(temp_dir)
                        github_utils.cleanup(temp_dir)  # Clean up the extracted files
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
                    
                    # Perform the search and extraction
                    result += search_and_extract(text_data, tag_name, file_type, uploaded_file.name)
                    
                    # Clear the text data to free up memory
                    del text_data
                    import gc
                    gc.collect()  # Force garbage collection after each file

                return Response({"results": result}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)  # Ensure the temporary directory is cleaned up
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def read_all_files_in_directory(self, directory):
        text_data = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.txt'):
                    with open(file_path, 'r') as f:
                        text_data.append(f.read())
                # Add more conditions here if needed for other file types within zip
        return text_data

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
        return text_data

    def extract_text_from_docx(self, docx_path):
        doc = docx.Document(docx_path)
        return [para.text for para in doc.paragraphs]

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
        return text_data
