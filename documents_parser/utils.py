import os
import zipfile
import git
import tempfile
import shutil
import os
import re
import numpy as np
from datetime import datetime


class GitHubUtils:
    def __init__(self):
        self.exclude_dirs = {'.git', '.github', '__pycache__'}
        self.exclude_files = {'.gitignore',
                              '.gitattributes', 'LICENSE', 'requirements.txt'}
        pass

    def clone_repo(self, github_url):
        temp_dir = tempfile.mkdtemp()
        git.Repo.clone_from(github_url, temp_dir)
        return temp_dir

    def read_zip_file(self, zip_path):
        """
        Read and process the contents of a ZIP file.
        """
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        text_data = self.read_all_files(temp_dir)
        shutil.rmtree(temp_dir)
        return text_data

    def read_all_files(self, repo_path):
        text_data = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            print(dirs)
            for file in files:
                if file in self.exclude_files or file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_data.append(f.read())
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")
        return text_data

    def cleanup(self, path):
        if path and os.path.exists(path):
            shutil.rmtree(path, onerror=self._handle_remove_readonly)

    def _handle_remove_readonly(self, func, path, exc_info):
        os.chmod(path, 0o700)
        func(path)



def clean_text(text):
    
    pattern = r'[^a-zA-Z0-9\s.,!?;:\'\"()-]'
    
    # Remove all characters that do not match the pattern
    cleaned_text = re.sub(pattern, '', text)
    
    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

def search_and_extract(source_text, tag, file_type, file_name, user="Test_User"):
    
    sentence_pattern = re.compile(r'([^.?!]*\b' + re.escape(tag) + r'\b[^.?!]*[.?!])', re.IGNORECASE)

    exact_matches = re.findall(sentence_pattern, source_text)

    partial_matches = re.findall(r'([^.?!]*\w*' + re.escape(tag) + r'\w*[^.?!]*[.?!])', source_text, re.IGNORECASE)

    extracted_data = []

    for match in exact_matches:
        highlighted_sentence = re.sub(rf"({tag})", r'**\1**', match, flags=re.IGNORECASE)
        extracted_data.append({
            "Source File Name": file_name,
            "File Type": file_type,
            "Tag Searched": tag,
            "Block/Record Tag Found": highlighted_sentence,
            "Location of the Tag": "Page 1, Section 2",  # Placeholder for actual location logic
            "Date of Search": datetime.now().strftime("%B %d, %Y"),
            "Search Author": user,
            "Other": "Exact match"
        })

    for match in partial_matches:
        if match.lower() != tag.lower():  
            highlighted_sentence = re.sub(rf"({tag})", r'**\1**', match, flags=re.IGNORECASE)
            extracted_data.append({
                "Source File Name": file_name,
                "File Type": file_type,
                "Tag Searched": tag,
                "Block/Record Tag Found": highlighted_sentence,
                "Location of the Tag": "Page 1, Section 2",  # Placeholder for actual location logic
                "Date of Search": datetime.now().strftime("%B %d, %Y"),
                "Search Author": user,
                "Other": "Partial match"
            })

    return extracted_data


# import pdfplumber
# import pytesseract
# from PIL import Image, ImageEnhance, ImageFilter, ImageOps
# import re
# import numpy as np

# class PDFTextExtractor:
#     def __init__(self, file_path, header_height=100):
#         self.file_path = file_path
#         self.header_height = header_height

#     def preprocess_image(self, image):
#         image = image.convert('L')
#         image = ImageOps.autocontrast(image)
#         enhancer = ImageEnhance.Contrast(image)
#         image = enhancer.enhance(2)
#         image = image.filter(ImageFilter.SHARPEN)
#         return image

#     def crop_image_to_remove_header(self, image):
#         width, height = image.size
#         cropped_image = image.crop((0, self.header_height, width, height))
#         return cropped_image

#     def extract_text_with_ocr(self):
#         text = ""
#         with pdfplumber.open(self.file_path) as pdf:
#             for page in pdf.pages:
#                 image = page.to_image(resolution=400).original
#                 pil_image = Image.fromarray(np.array(image))
#                 cropped_image = self.crop_image_to_remove_header(pil_image)
#                 processed_image = self.preprocess_image(cropped_image)
#                 custom_oem_psm_config = r'--oem 3 --psm 6'
#                 text += pytesseract.image_to_string(processed_image, lang='ara+eng', config=custom_oem_psm_config)
#         return text

#     @staticmethod
#     def extract_arabic(text):
#         arabic_text = re.findall(r'[\u0600-\u06FF]+', text)
#         return ' '.join(arabic_text)
