import uuid
import fitz  
from PIL import Image
import pytesseract
from spire.pdf import *
from spire.pdf.common import *
import concurrent.futures
import re
import numpy as np
import pdfplumber
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import threading
from datetime import datetime
import shutil
import subprocess

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


def rename_docx_file(docx_path):

    file_name=docx_path.split(".")[0]
    random_filename = f"{file_name}_{uuid.uuid1()}.docx"
    temp_docx_path = os.path.join("/tmp", random_filename)

    # Copy and rename the original DOCX file to the new path
    shutil.copy(docx_path, temp_docx_path)
    
    return temp_docx_path

def convert_docx_to_pdf_with_libreoffice(temp_docx_path):
    """
    Convert a renamed DOCX file to a PDF using LibreOffice and keep the original filename.
    """
    # Define the output directory
    output_dir = "/tmp"
    temp_docx_path=rename_docx_file(temp_docx_path)
    # Convert DOCX to PDF using LibreOffice command-line tool
    try:
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, temp_docx_path],
            check=True, capture_output=True, text=True
        )
        print(result.stdout)  # Debugging: Print stdout from the command
        print(result.stderr)  # Debugging: Print stderr from the command
    except subprocess.CalledProcessError as e:
        print("Error during LibreOffice conversion:", e)
        print(e.stdout)  # Capture standard output
        print(e.stderr)  # Capture standard error
        raise

    # The output PDF will be saved with the same base name as the input file
    input_base_name = os.path.splitext(os.path.basename(temp_docx_path))[0]
    converted_pdf_path = os.path.join(output_dir, f"{input_base_name}.pdf")

    # Ensure the PDF file exists and is not empty
    if not os.path.exists(converted_pdf_path) or os.path.getsize(converted_pdf_path) == 0:
        raise FileNotFoundError(f"Conversion failed: Output PDF not created or is empty at {converted_pdf_path}")

    # Return the path of the generated PDF file
    return converted_pdf_path

def read_doc_with_fitz(pdf_path):
    """
    Read a PDF file from disk using PyMuPDF (fitz) and extract text line by line.
    """
    # Open the PDF from disk using PyMuPDF
    pdf_document = fitz.open(pdf_path)
        
    extracted_text = {}
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        extracted_text[f"page {page_num + 1}"] = page.get_text("text")
    pdf_document.close()

    # Delete the PDF file after processing
    os.remove(pdf_path)
    
    return extracted_text






def search_pdf(text_dict, tag, file_name,file_type,user="Test_User"):
    extracted_data_exact = []
    extracted_data_partial = []

    for page_num, text in text_dict.items():
        lines = [line for line in text.splitlines() if line.strip()]
        for line_index, line_text in enumerate(lines):
            if line_text.strip():
                exact_matches = list(re.finditer(rf"\b{re.escape(tag)}\b", line_text, re.IGNORECASE))
                partial_matches = list(re.finditer(rf"\w*{re.escape(tag)}\w*", line_text, re.IGNORECASE))
                
                # Process exact matches
                for match in exact_matches:
                    extracted_data_exact.append({
                        "Source File Name": file_name,
                        "File Type": f"{file_type}",
                        "Tag Searched": tag,
                        "Block/Record": line_text.strip(),
                        "Location of the Tag": f"{page_num}, Line {line_index + 1}",
                        "Date of Search": datetime.now().strftime("%B %d, %Y %H:%M:%S"),
                        "Search Author": user,
                        "Other": ""
                    })
                
                # Process partial matches
                for match in partial_matches:
                    matched_text = match.group()
                    if matched_text.lower() != tag.lower():  # Exclude exact matches
                        extracted_data_partial.append({
                            "Source File Name": file_name,
                            "File Type": f"{file_type}",
                            "Tag Searched": tag,
                            "Block/Record": line_text.strip(),
                            "Location of the Tag": f"{page_num}, Line {line_index + 1}",
                            "Date of Search": datetime.now().strftime("%B %d, %Y %H:%M:%S"),
                            "Search Author": user,
                            "Other": ""
                        })

    return extracted_data_exact, extracted_data_partial

def read_pdf_file(file_path):
    type_= determine_pdf_type(file_path)
    if type_ =="text":
        text_data=extract_text_with_format(file_path)
    else:
        text_data=extract_text_with_ocr(file_path)
        
    return text_data


def read_doc_file(file_path):
    pdf_buffer=convert_docx_to_pdf_with_libreoffice(file_path)
    text_data=read_doc_with_fitz(pdf_buffer)
    return text_data
