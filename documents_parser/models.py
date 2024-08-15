from django.db import models

# Create your models here.
import pdfplumber
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import re
import numpy as np

class PDFTextExtractor:
    def __init__(self, file_path, header_height=100):
        self.file_path = file_path
        self.header_height = header_height

    def preprocess_image(self, image):
        image = image.convert('L')
        image = ImageOps.autocontrast(image)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)
        image = image.filter(ImageFilter.SHARPEN)
        return image

    def crop_image_to_remove_header(self, image):
        width, height = image.size
        cropped_image = image.crop((0, self.header_height, width, height))
        return cropped_image

    def extract_text_with_ocr(self):
        text = ""
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                image = page.to_image(resolution=400).original
                pil_image = Image.fromarray(np.array(image))
                cropped_image = self.crop_image_to_remove_header(pil_image)
                processed_image = self.preprocess_image(cropped_image)
                custom_oem_psm_config = r'--oem 3 --psm 6'
                text += pytesseract.image_to_string(processed_image, lang='ara+eng', config=custom_oem_psm_config)
        return text

    @staticmethod
    def extract_arabic(text):
        arabic_text = re.findall(r'[\u0600-\u06FF]+', text)
        return ' '.join(arabic_text)
