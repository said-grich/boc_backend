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
from .utils import *


def clean_text_git(text):
    
    pattern = r'[^a-zA-Z0-9\s.,!?;:\'\"()-]'
    
    # Remove all characters that do not match the pattern
    cleaned_text = re.sub(pattern, '', text)
        
    return cleaned_text

def read_all_files_in_directory(directory):
    text_data = []
    binary_extensions = ['.dll', '.exe', '.bin', '.dat', '.o', '.so', '.class', '.pyc', '.pyo', '.a', '.lib', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.zip', '.gz','yml',".jar",".class"]
    data_dict={}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.startswith('.') or any(file.lower().endswith(ext) for ext in binary_extensions):
                print(f"Skipping excluded or binary file: {file_path}")
                continue
            print(f"Processing file: {file_path}")
            data_dict[file]={}
            data_dict[file]["content"]=""
            # try:
            if file.lower().endswith('.docx'):
                
                extracted_text = extract_text_from_docx(file_path)
                if extracted_text: 
                    data_dict[file]["content"]=extracted_text
            elif file.lower().endswith('.xls') or file.lower().endswith('.xlsx'):
                extracted_text = extract_text_from_excel(file_path)
                if extracted_text:  
                    data_dict[file]["content"]=extracted_text
            else:
                
                with open(file_path, 'rb') as f:
                    raw_data = f.read()

                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                    confidence = result['confidence']

                    if encoding is None or confidence < 0.5:
                        # print(f"Skipping file with undetectable or low confidence encoding: {file_path}")
                        continue

                    try:
                        with open(file_path, 'r', encoding=encoding, errors='ignore') as text_file:
                            content = text_file.read()
                            data_dict[file]["content"]=content
                    except UnicodeDecodeError as e:
                        print(f"UnicodeDecodeError reading {file_path} with encoding {encoding}: {e}")
                        continue
    return data_dict

def search_github(tag,zip_name,data_dict , user="Test_User"):
    extracted_data_exact=[]
    extracted_data_partial=[]
    for file_name in data_dict.keys():
        
        content=data_dict[file_name]["content"];
        file_type=file_name.split(".")[-1]
        
        exact_matches = list(re.finditer(rf"\b{re.escape(tag)}\b", content, re.IGNORECASE))
        partial_matches = list(re.finditer(rf"\w*{re.escape(tag)}\w*", content, re.IGNORECASE))

        for match in exact_matches:
            match_start = match.start()
            match_end = match.end()
            
            highlighted_sentence = find_line_by_indices(content,match_start,match_end)
            
            line_number,col_number=find_column_in_line(content, highlighted_sentence, tag)
            extracted_data_exact.append({
                "Source File Name": f"{zip_name}/{file_name}",
                "File Type": file_type,
                "Tag Searched": tag,
                "Block/Record": highlighted_sentence,
                "Location of the Tag": f"{file_name} (Ln {line_number}, Col {col_number[0]})",
                "Date of Search": datetime.now().strftime("%B %d, %Y"),
                "Search Author": user,
                "Other": ""
            })

        for match in partial_matches:
            matched_text = match.group()
            if matched_text.lower() != tag.lower():  
                match_start = match.start()
                match_end = match.end()
    
                highlighted_sentence = find_line_by_indices(content,match_start,match_end)
                
                line_number,col_number=find_column_in_line(content, highlighted_sentence, tag)
                extracted_data_partial.append({
                    "Source File Name": f"{zip_name}/{file_name}",
                    "File Type": file_type,
                    "Tag Searched": tag,
                    "Block/Record": highlighted_sentence,
                    "Location of the Tag": f"{file_name} (Ln {line_number}, Col {col_number[0]})",
                    "Date of Search": datetime.now().strftime("%B %d, %Y"),
                    "Search Author": user,
                    "Other": "Partial match"
                })

    return extracted_data_exact , extracted_data_partial



def find_line_by_indices(text, tag_start, tag_end):
    # Validate inputs
    if not isinstance(text, str):
        raise ValueError("The 'text' should be of type 'str'.")
    if not isinstance(tag_start, int) or not isinstance(tag_end, int):
        raise ValueError("Both 'tag_start' and 'tag_end' should be of type 'int'.")
    if tag_start < 0 or tag_end > len(text) or tag_start > tag_end:
        raise ValueError("Invalid 'tag_start' or 'tag_end' indices.")

    # Find the line containing the tag
    line_start = text.rfind('\n', 0, tag_start) + 1
    line_end = text.find('\n', tag_end)
    
    if line_end == -1:
        line_end = len(text)  # If no newline is found, set to end of text

    line = text[line_start:line_end]

    return line.strip()




def find_column_in_line(text, line_to_find, tag):

    
    if not isinstance(text, str) or not isinstance(line_to_find, str) or not isinstance(tag, str):
        raise ValueError("All inputs ('text', 'line_to_find', and 'tag') should be of type 'str'.")

    # Normalize inputs by stripping leading/trailing whitespace
    line_to_find = line_to_find.strip()
    tag = tag.strip()

    # Split the text into lines
    lines = text.splitlines()

    # Initialize the current position in the text and line number
    current_position = 0
    line_number = 0

    # Iterate over lines in the text
    for index_line,line in enumerate(lines):
        line_number += 1
        line_length = len(line)
        
        # Check if the current line matches the line we are searching for
        if line.strip() == line_to_find:
            start_index = current_position
            end_index = start_index + line_length
            
            # Find the tag within the line
            tag_start = line.lower().find(tag.lower())
            
            if tag_start != -1:
                # Calculate the start and end column positions of the tag within the line
                start_column = tag_start + 1  # Convert to 1-based index
                end_column = start_column + len(tag) - 1
                return (line_number, (start_column, end_column))
        
        # Update the current position (including newline character)
        current_position += line_length + 1  # +1 for the newline character
    
    return (-1, (-1, -1))
