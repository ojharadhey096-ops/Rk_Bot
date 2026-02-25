import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import re
import unicodedata

class HindiOCREngine:
    def __init__(self):
        # Configure Tesseract path if needed (for Windows)
        if os.name == 'nt':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def preprocess_image(self, image_path, enhance=False):
        """Preprocess image for better Hindi OCR accuracy"""
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Noise removal
        if enhance:
            gray = cv2.medianBlur(gray, 3)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Deskew correction
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            thresh, M, (w, h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        
        # Increase contrast
        if enhance:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            rotated = clahe.apply(rotated)
        
        # Remove borders
        contour_img = cv2.copyMakeBorder(rotated, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[0,0,0])
        contours, _ = cv2.findContours(contour_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            max_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_contour)
            rotated = contour_img[y:y+h, x:x+w]
        
        # Resize for better OCR (300 DPI equivalent)
        scale_factor = 2.0
        resized = cv2.resize(rotated, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        
        return resized
    
    def extract_text(self, image_path, enhance=False, lang='hin'):
        """Extract text from image using Tesseract OCR with Hindi language support"""
        preprocessed_img = self.preprocess_image(image_path, enhance)
        
        # Convert to PIL Image for pytesseract
        pil_image = Image.fromarray(preprocessed_img)
        
        # Extract text
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(pil_image, lang=lang, config=custom_config)
        
        # Unicode normalization and post-processing
        normalized_text = self.normalize_text(text)
        
        return normalized_text
    
    def normalize_text(self, text):
        """Normalize and clean extracted Hindi text"""
        # Unicode normalization
        normalized = unicodedata.normalize('NFKC', text)
        
        # Remove broken characters
        normalized = re.sub(r'[^\u0000-\u007F\u0900-\u097F\s]', '', normalized)
        
        # Fix common OCR mistakes
        replacements = {
            '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
            '5': '५', '6': '६', '7': '७', '8': '८', '9': '९',
            '|': '।', '-': '—', '`': '‘', "'": '’',
            '\"': '“', '\"': '”'
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove duplicate spaces and normalize line breaks
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = re.sub(r'\n\s*', '\n', normalized)
        
        # Fix Hindi matras (optional but improves readability)
        normalized = self.fix_matras(normalized)
        
        return normalized.strip()
    
    def fix_matras(self, text):
        """Fix common Hindi matra issues from OCR"""
        # Fix missing or broken matras
        matra_fixes = {
            'ा ': 'ा', 'े ': 'े', 'ै ': 'ै',
            'ो ': 'ो', 'ौ ': 'ौ', 'ी ': 'ी'
        }
        
        for old, new in matra_fixes.items():
            text = text.replace(old, new)
        
        return text
    
    def get_ocr_confidence(self, image_path):
        """Get OCR confidence score (0-100)"""
        try:
            data = pytesseract.image_to_data(
                Image.open(image_path),
                lang='hin',
                output_type=pytesseract.Output.DICT
            )
            
            confidences = []
            for i, conf in enumerate(data['conf']):
                if conf != -1 and data['text'][i].strip():
                    confidences.append(int(conf))
            
            if confidences:
                return sum(confidences) / len(confidences)
            return 0
        except Exception as e:
            print(f"Error getting confidence: {e}")
            return 0


class MCQDetector:
    """Detect and extract Hindi MCQs from text"""
    
    def __init__(self):
        # Question patterns (Hindi and English)
        self.question_patterns = [
            r'प्रश्न\s*(\d+)\.',
            r'Q\.?\s*(\d+)',
            r'(\d+)\.',
            r'\((\d+)\)'
        ]
        
        # Option patterns (Hindi and English)
        self.option_patterns = [
            r'[A-Da-d]\)',
            r'[A-Da-d]\.',
            r'\((क|ख|ग|घ|च|छ|ज|झ)\)',
            r'(\d+)\.'
        ]
    
    def extract_questions(self, text):
        """Extract structured questions from text"""
        questions = []
        
        # Split text into question candidates
        lines = text.split('\n')
        current_question = None
        current_options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains a question number
            question_match = None
            for pattern in self.question_patterns:
                match = re.search(pattern, line)
                if match:
                    question_match = match
                    break
            
            if question_match:
                # Save previous question
                if current_question and current_options:
                    questions.append({
                        'question_number': current_question['number'],
                        'question_text': current_question['text'].strip(),
                        'options': [opt.strip() for opt in current_options],
                        'correct_answer': None
                    })
                
                # Start new question
                question_number = question_match.group(1)
                question_text = re.sub(r'^.*?(?=[^\d\W])', '', line)
                current_question = {
                    'number': question_number,
                    'text': question_text
                }
                current_options = []
            else:
                # Check if line contains an option
                option_match = None
                for pattern in self.option_patterns:
                    match = re.match(pattern, line)
                    if match:
                        option_match = match
                        break
                
                if option_match and current_question:
                    # Extract option text
                    option_text = line[len(option_match.group(0)):].strip()
                    current_options.append(option_text)
                elif current_question:
                    # Add to question text if it's a continuation
                    current_question['text'] += ' ' + line
        
        # Save last question
        if current_question and current_options:
            questions.append({
                'question_number': current_question['number'],
                'question_text': current_question['text'].strip(),
                'options': [opt.strip() for opt in current_options],
                'correct_answer': None
            })
        
        return questions
    
    def detect_correct_answer(self, question_text, options):
        """Detect correct answer from question text (experimental)"""
        answer_patterns = [
            r'सही उत्तर\s*[:=]\s*([A-Da-d]|\(?(क|ख|ग|घ)\)?)',
            r'Answer\s*[:=]\s*([A-Da-d]|\(?(क|ख|ग|घ)\)?)'
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, question_text)
            if match:
                answer = match.group(1).strip().upper()
                return self.normalize_answer(answer)
        
        return None
    
    def normalize_answer(self, answer):
        """Normalize answer format"""
        answer_map = {
            'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D',
            'क': 'A', 'ख': 'B', 'ग': 'C', 'घ': 'D',
            'च': 'E', 'छ': 'F', 'ज': 'G', 'झ': 'H'
        }
        
        return answer_map.get(answer.strip('()'), None)
