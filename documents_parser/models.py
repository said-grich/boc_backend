import fitz  
from PIL import Image
import pytesseract
from spire.pdf import *
from spire.pdf.common import *
from transformers import pipeline
import concurrent.futures
import re
import numpy as np
import pdfplumber
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import threading
from datetime import datetime

semaphore = None

def determine_pdf_type(file_path):
    try:
        # Attempt to extract text using PyMuPDF (fitz)
        doc = fitz.open(file_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():  # Check if any text is extracted
                return "text"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    
    return "image"

def extract_text_with_format(file_path):
    doc = fitz.open(file_path)
    results_text = {}
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        results_text [f"page {page_num+1}"]= page.get_text()
    return results_text



semaphore = None

def init_semaphore(max_workers):
    global semaphore
    semaphore = threading.BoundedSemaphore(value=max_workers)

def preprocess_image(image, enhance_contrast=True, sharpen_image=False, reduce_noise=True, thresholding=True):
    """
    Preprocess the image to improve OCR accuracy.
    """
    image = image.convert('L')  # Convert to grayscale
    
    if reduce_noise:
        image = image.filter(ImageFilter.MedianFilter())  # Apply median filter to reduce noise
    
    if enhance_contrast:
        image = ImageOps.autocontrast(image)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
    
    if thresholding:
        image = image.point(lambda p: p > 128 and 255)  # Simple thresholding
    
    if sharpen_image:
        image = image.filter(ImageFilter.SHARPEN)
    
    return image


def crop_image_to_remove_header(image, header_height):
    width, height = image.size
    if header_height > 0:
        cropped_image = image.crop((0, header_height, width, height))
    else:
        cropped_image = image
    return cropped_image

def process_page(page, resolution, header_height, enhance_contrast, sharpen_image):
    """
    Process a single PDF page to extract text using OCR.
    """
    global semaphore
    try:
        semaphore.acquire()  # Acquire a semaphore to limit concurrent processing
        image = page.to_image(resolution=resolution).original
        pil_image = Image.fromarray(np.array(image))
        cropped_image = crop_image_to_remove_header(pil_image, header_height)
        processed_image = preprocess_image(cropped_image, enhance_contrast, sharpen_image)
        custom_oem_psm_config = r'--oem 3 --psm 3'
        text = pytesseract.image_to_string(processed_image, lang='eng+fra+spa+nld', config=custom_oem_psm_config)
    finally:
        semaphore.release()  # Release the semaphore after processing
    return text

def extract_text_with_ocr(file_path, header_height=5, resolution=300, enhance_contrast=True, sharpen_image=True, use_parallel=False, max_workers=4):
   
    init_semaphore(max_workers)  
    page_text_dict = {}

    with pdfplumber.open(file_path) as pdf:
        if use_parallel:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = executor.map(
                    lambda page: process_page(page, resolution, header_height, enhance_contrast, sharpen_image), pdf.pages
                )
                page_text_dict = {f"page {page_num+1}": text for page_num, text in enumerate(results)}
        else:
            for page_num, page in enumerate(pdf.pages):
                page_number = f"page {page_num + 1}"
                text = process_page(page, resolution, header_height, enhance_contrast, sharpen_image)
                page_text_dict[page_number] = text

    return page_text_dict





def search_pdf(text_dict, tag, file_name, user="Test_User"):
    extracted_data_exact = []
    extracted_data_partial = []

    for page_num, text in text_dict.items():
        lines = [line for line in text.splitlines() if line.strip()]
        for line_index, line_text in enumerate(lines):
            if line_text.strip():
                print(line_text ,"=============>" +str(line_index)) # Only process non-empty lines
                exact_matches = list(re.finditer(rf"\b{re.escape(tag)}\b", line_text, re.IGNORECASE))
                partial_matches = list(re.finditer(rf"\w*{re.escape(tag)}\w*", line_text, re.IGNORECASE))
                
                # Process exact matches
                for match in exact_matches:
                    extracted_data_exact.append({
                        "Source File Name": file_name,
                        "File Type": 'Pdf',
                        "Tag Searched": tag,
                        "Block/Record": line_text.strip(),
                        "Location of the Tag": f"{page_num}, Line {line_index + 1}",
                        "Date of Search": datetime.now().strftime("%B %d, %Y"),
                        "Search Author": user,
                        "Other": ""
                    })
                
                # Process partial matches
                for match in partial_matches:
                    matched_text = match.group()
                    if matched_text.lower() != tag.lower():  # Exclude exact matches
                        extracted_data_partial.append({
                            "Source File Name": file_name,
                            "File Type": 'Pdf',
                            "Tag Searched": tag,
                            "Block/Record": line_text.strip(),
                            "Location of the Tag": f"{page_num}, Line {line_index + 1}",
                            "Date of Search": datetime.now().strftime("%B %d, %Y"),
                            "Search Author": user,
                            "Other": "partial"
                        })

    return extracted_data_exact, extracted_data_partial

def read_pdf_file(file_path,tag, file_name, user="Test_User"):
    type_= determine_pdf_type(file_path)
    if type_ =="text":
        text_data=extract_text_with_format(file_path)
    else:
        text_data=extract_text_with_ocr(file_path)
        
    return search_pdf(text_data, tag, file_name, user="Test_User")