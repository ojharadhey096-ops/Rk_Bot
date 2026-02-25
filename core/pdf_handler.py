import os
import tempfile
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
import fitz  # pymupdf
import cv2
import numpy as np

class PDFHandler:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def is_text_based(self, pdf_path):
        """Check if PDF is text-based or scanned"""
        try:
            # Try to extract text with pdfminer
            text = extract_text(pdf_path)
            if text.strip() and len(text.strip()) > 100:
                return True
        except Exception as e:
            print(f"PDF text extraction error: {e}")
        
        try:
            # Try with PyMuPDF (fitz)
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            if text.strip() and len(text.strip()) > 100:
                return True
        except Exception as e:
            print(f"PyMuPDF text extraction error: {e}")
        
        return False
    
    def extract_text_from_text_pdf(self, pdf_path):
        """Extract text from text-based PDF"""
        try:
            # Use PyMuPDF for better text extraction
            doc = fitz.open(pdf_path)
            full_text = []
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                full_text.append(f"=== Page {page_num + 1} ===\n{text}")
            
            return "\n".join(full_text)
        except Exception as e:
            print(f"PDF text extraction error: {e}")
            return ""
    
    def convert_scanned_pdf_to_images(self, pdf_path, dpi=300):
        """Convert scanned PDF pages to images"""
        try:
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                output_folder=self.temp_dir,
                fmt='png',
                thread_count=4
            )
            
            image_paths = []
            for i, img in enumerate(images):
                img_path = os.path.join(self.temp_dir, f"page_{i+1}.png")
                img.save(img_path, 'PNG')
                image_paths.append(img_path)
            
            return image_paths
        except Exception as e:
            print(f"PDF to image conversion error: {e}")
            return []
    
    def extract_text_from_scanned_pdf(self, pdf_path, ocr_engine):
        """Extract text from scanned PDF using OCR"""
        page_texts = []
        image_paths = self.convert_scanned_pdf_to_images(pdf_path)
        
        for i, img_path in enumerate(image_paths):
            try:
                text = ocr_engine.extract_text(img_path)
                page_texts.append({
                    'page_number': i + 1,
                    'text': text,
                    'confidence': ocr_engine.get_ocr_confidence(img_path)
                })
            except Exception as e:
                print(f"Page {i+1} OCR error: {e}")
                page_texts.append({
                    'page_number': i + 1,
                    'text': '',
                    'confidence': 0
                })
        
        # Clean up temp images
        for img_path in image_paths:
            try:
                os.remove(img_path)
            except:
                pass
        
        return page_texts
    
    def extract_text_from_pdf(self, pdf_path, ocr_engine):
        """Extract text from any PDF (text-based or scanned)"""
        if self.is_text_based(pdf_path):
            return {
                'type': 'text',
                'pages': [{'page_number': 1, 'text': self.extract_text_from_text_pdf(pdf_path), 'confidence': 100}]
            }
        else:
            return {
                'type': 'scanned',
                'pages': self.extract_text_from_scanned_pdf(pdf_path, ocr_engine)
            }
    
    def cleanup(self):
        """Clean up temporary directory"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Cleanup error: {e}")
