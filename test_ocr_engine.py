#!/usr/bin/env python3
"""
Test script for the Hindi OCR Engine
This script demonstrates the OCR pipeline with sample data
"""

import os
import sys
import tempfile
from core.ocr_engine import HindiOCREngine, MCQDetector
from core.test_generator import TestGenerator

def main():
    print("🚀 RADHEY AI LIFE OS - OCR Engine Test")
    print("=" * 50)
    
    # Test OCR Engine
    print("\n🔍 Testing OCR Engine...")
    
    try:
        ocr_engine = HindiOCREngine()
        mcq_detector = MCQDetector()
        test_generator = TestGenerator()
        
        print("✅ OCR engine initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing OCR engine: {e}")
        print("\n🔧 Troubleshooting Steps:")
        print("1. Check if Tesseract OCR is installed")
        print("2. Verify Hindi language pack (hin.traineddata) is installed")
        print("3. Check TESSERACT_PATH environment variable")
        return False
    
    # Test Tesseract installation
    print("\n📝 Testing Tesseract installation...")
    
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is available")
        
        # Check if Hindi language pack is installed
        from PIL import Image
        import numpy as np
        
        # Create a temporary image with Hindi text
        import cv2
        
        # Create a test image
        img = np.ones((100, 400, 3), dtype=np.uint8) * 255
        
        # Add some Hindi text (simplified for testing)
        cv2.putText(img, 'नमस्ते दुनिया', (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, 
                   cv2.LINE_AA)
        
        temp_img_path = os.path.join(tempfile.mkdtemp(), 'test_hindi.png')
        cv2.imwrite(temp_img_path, img)
        
        print("✅ Temporary test image created at:", temp_img_path)
        
        # Test OCR
        try:
            extracted_text = ocr_engine.extract_text(temp_img_path, enhance=False)
            print(f"📄 Extracted Text: {repr(extracted_text.strip())}")
            
            if len(extracted_text.strip()) > 0:
                print("✅ OCR extraction succeeded")
            else:
                print("⚠️ OCR extraction returned empty text")
            
        except Exception as e:
            print(f"❌ OCR extraction error: {e}")
            print("\n🔍 Common Issues:")
            print("1. Hindi language pack (hin.traineddata) not installed")
            print("2. Tesseract path not configured correctly")
            print("3. Image preprocessing issues")
            
        finally:
            # Cleanup
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
        
    except Exception as e:
        print(f"❌ Tesseract not found: {e}")
        print("\n🔧 Installation Instructions:")
        print("Ubuntu/Debian: sudo apt install tesseract-ocr tesseract-ocr-hin")
        print("macOS: brew install tesseract tesseract-lang")
        return False
    
    # Test MCQ Detection
    print("\n🎯 Testing MCQ Detection...")
    
    sample_text = """
प्रश्न 1. एक संख्या का 20% 25 है तो वह संख्या क्या है?
A) 100
B) 125
C) 150
D) 175

प्रश्न 2. सौरमंडल में कितने ग्रह हैं?
क) 8
ख) 9
ग) 10
घ) 12

Q.3. Which of these is the largest planet?
A) Earth
B) Jupiter
C) Saturn
D) Neptune
"""
    
    try:
        questions = mcq_detector.extract_questions(sample_text)
        print(f"✅ Detected {len(questions)} questions")
        
        for i, q in enumerate(questions):
            print(f"\nQ{i+1}: {q['question_text']}")
            for j, opt in enumerate(q['options']):
                print(f"   {chr(65+j)}) {opt}")
                
    except Exception as e:
        print(f"❌ MCQ detection error: {e}")
    
    # Test Test Generator
    print("\n📚 Testing Test Generator...")
    
    try:
        # Create some sample questions
        sample_questions = [
            {
                'question_number': '1',
                'question_text': 'हिंदी भाषा का जन्म कहाँ हुआ?',
                'options': ['उत्तर प्रदेश', 'बिहार', 'मध्य प्रदेश', 'उत्तराखंड'],
                'correct_answer': 'B'
            },
            {
                'question_number': '2',
                'question_text': 'नई दिल्ली किस वर्ष राजधानी बनी?',
                'options': ['1901', '1911', '1921', '1931'],
                'correct_answer': 'B'
            },
            {
                'question_number': '3',
                'question_text': 'गंगा नदी का उद्गम स्थल कहाँ है?',
                'options': ['हिमालय', 'विंध्य', 'सतपुड़ा', 'अरावली'],
                'correct_answer': 'A'
            }
        ]
        
        # Generate HTML quiz
        temp_dir = tempfile.mkdtemp()
        quiz_file = test_generator.generate_html_quiz(
            sample_questions,
            filename=os.path.join(temp_dir, 'sample_quiz.html'),
            timer=60
        )
        
        print(f"✅ HTML quiz generated at: {quiz_file}")
        
        # Generate JSON export
        json_file = test_generator.generate_json_export(
            sample_questions,
            filename=os.path.join(temp_dir, 'sample_questions.json')
        )
        print(f"✅ JSON export generated at: {json_file}")
        
        # Generate ZIP export
        zip_file = test_generator.generate_zip_export(
            sample_questions,
            base_filename=os.path.join(temp_dir, 'sample_quiz')
        )
        print(f"✅ ZIP export generated at: {zip_file}")
        
        # Verify files are created
        all_good = True
        for file_path in [quiz_file, json_file, zip_file]:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"✅ {os.path.basename(file_path)} is valid")
            else:
                print(f"❌ {os.path.basename(file_path)} is invalid or empty")
                all_good = False
                
        if all_good:
            print("✅ All test generator functions passed")
        else:
            print("❌ Some test generator functions failed")
            
    except Exception as e:
        print(f"❌ Test generator error: {e}")
    
    # Test Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    
    # Check if requirements are met
    print("\n📦 Checking Requirements:")
    
    required_packages = [
        'pytesseract', 'PIL', 'opencv-python', 'pdf2image', 
        'pdfminer.six', 'pymupdf', 'numpy', 'python-dotenv',
        'pymongo', 'celery', 'redis', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            missing_packages.append(package)
            
    if missing_packages:
        print(f"\n🔧 Missing packages to install: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
    
    print("\n🎉 Test completed!")
    print("\n📚 Next Steps:")
    print("1. Configure Telegram bot token in .env file")
    print("2. Set up MongoDB connection")
    print("3. Run the bot: python bot/main.py")
    
    return len(missing_packages) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
