import concurrent.futures
import re
import numpy as np
import pdfplumber
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import threading

# Global semaphore for limiting concurrent processing
semaphore = None

def init_semaphore(max_workers):
    global semaphore
    semaphore = threading.BoundedSemaphore(value=max_workers)

def preprocess_image(image, enhance_contrast=True, sharpen_image=False):
    image = image.convert('L')  # Convert to grayscale
    if enhance_contrast:
        image = ImageOps.autocontrast(image)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
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
    global semaphore
    try:
        semaphore.acquire()  # Acquire a semaphore to limit concurrent processing
        image = page.to_image(resolution=resolution).original
        pil_image = Image.fromarray(np.array(image))
        cropped_image = crop_image_to_remove_header(pil_image, header_height)
        processed_image = preprocess_image(cropped_image, enhance_contrast, sharpen_image)
        custom_oem_psm_config = r'--oem 3 --psm 3'
        text = pytesseract.image_to_string(processed_image, lang='ara+eng', config=custom_oem_psm_config)
    finally:
        semaphore.release()  # Release the semaphore after processing
    return text

def extract_text_with_ocr(file_path, header_height=50, resolution=200, enhance_contrast=True, sharpen_image=False, use_parallel=True, max_workers=4):
    init_semaphore(max_workers)  # Initialize the semaphore
    text = ""
    with pdfplumber.open(file_path) as pdf:
        if use_parallel:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = executor.map(lambda page: process_page(page, resolution, header_height, enhance_contrast, sharpen_image), pdf.pages)
                text = "".join(results)
        else:
            for page in pdf.pages:
                text += process_page(page, resolution, header_height, enhance_contrast, sharpen_image)
    return text

def extract_arabic(text):
    arabic_text = re.findall(r'[\u0600-\u06FF]+', text)
    return ' '.join(arabic_text)

# Example usage with a single file
def process_single_pdf(file_path):
    text = extract_text_with_ocr(
        file_path,
        header_height=50,
        resolution=200,
        enhance_contrast=True,
        sharpen_image=False,
        use_parallel=True,
        max_workers=2
    )
    
    # Do something with the text, e.g., save it to a file or database
    print(f"Processing completed for {file_path}")

    # Clear the OCR results from memory
    del text
    import gc
    gc.collect()  # Force garbage collection to free up memory

# Example usage with multiple files
def process_multiple_pdfs(file_paths):
    for file_path in file_paths:
        process_single_pdf(file_path)

