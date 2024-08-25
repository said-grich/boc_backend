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


def read_all_files_in_directory(self, directory):
    text_data = []
    binary_extensions = ['.dll', '.exe', '.bin', '.dat', '.o', '.so', '.class', '.pyc', '.pyo', '.a', '.lib', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.zip', '.gz','yml']

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            

            if file.startswith('.') or any(file.lower().endswith(ext) for ext in binary_extensions):
                print(f"Skipping excluded or binary file: {file_path}")
                continue
            print(f"Processing file: {file_path}")
            # try:
            if file.lower().endswith('.docx'):
                extracted_text = self.extract_text_from_docx(file_path)
                if extracted_text: 
                    text_data.append(extracted_text)
            elif file.lower().endswith('.xls') or file.lower().endswith('.xlsx'):
                extracted_text = self.extract_text_from_excel(file_path)
                print(extracted_text)

                if extracted_text:  
                    text_data.append(extracted_text)
            else:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()

                    # Use chardet to detect encoding
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                    confidence = result['confidence']

                    # Check if encoding is None or confidence is too low
                    if encoding is None or confidence < 0.5:
                        print(f"Skipping file with undetectable or low confidence encoding: {file_path}")
                        continue

                    # Try reading the file with the detected encoding
                    try:
                        with open(file_path, 'r', encoding=encoding, errors='ignore') as text_file:
                            content = text_file.read()
                            cleaned_content = clean_text(content)
                            if cleaned_content:  
                                text_data.append(cleaned_content)
                    except UnicodeDecodeError as e:
                        print(f"UnicodeDecodeError reading {file_path} with encoding {encoding}: {e}")
                        continue

            # except IOError as e:
            #     print(f"IOError reading {file_path}: {e}")
            #     continue

    return text_data