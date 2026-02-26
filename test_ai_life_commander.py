#!/usr/bin/env python3
"""
Comprehensive test script for RADHEY AI LIFE COMMANDER
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
from core.file_storage import get_file_storage
from core.media_merger import MediaMerger
from core.ocr_engine import HindiOCREngine
from core.pdf_handler import PDFHandler

class TestFileStorage(unittest.TestCase):
    """Test FileStorage functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.storage = get_file_storage()
        self.test_user_id = 99999
        
    def test_save_user(self):
        """Test user creation and retrieval"""
        self.storage.save_user(
            user_id=self.test_user_id,
            username='testuser',
            first_name='Test',
            last_name='User',
            chat_id=12345
        )
        
        user = self.storage.get_user(self.test_user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(user['first_name'], 'Test')
        self.assertEqual(user['last_name'], 'User')
        self.assertEqual(user['chat_id'], 12345)
    
    def test_task_management(self):
        """Test task creation and retrieval"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.storage.add_task(
            user_id=self.test_user_id,
            text='Test task 1',
            date=today,
            time='09:00'
        )
        
        tasks = self.storage.get_user_tasks(self.test_user_id)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['text'], 'Test task 1')
        self.assertEqual(tasks[0]['date'], today)
        self.assertEqual(tasks[0]['time'], '09:00')
        
    def test_habit_management(self):
        """Test habit creation and streak tracking"""
        self.storage.add_habit(
            user_id=self.test_user_id,
            name='Daily Walk',
            description='30 minute walk'
        )
        
        habits = self.storage.get_user_habits(self.test_user_id)
        self.assertEqual(len(habits), 1)
        self.assertEqual(habits[0]['name'], 'Daily Walk')
        self.assertEqual(habits[0]['description'], '30 minute walk')
        
        # Test marking habit as done
        today = datetime.now().strftime('%Y-%m-%d')
        self.storage.mark_habit_done(self.test_user_id, 0, today)
        
        habits = self.storage.get_user_habits(self.test_user_id)
        self.assertEqual(habits[0]['streak'], 1)
    
    def test_expense_management(self):
        """Test expense creation and retrieval"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.storage.add_expense(
            user_id=self.test_user_id,
            amount=100.50,
            category='Food',
            description='Lunch'
        )
        
        expenses = self.storage.get_user_expenses(self.test_user_id)
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0]['amount'], 100.50)
        self.assertEqual(expenses[0]['category'], 'Food')
        self.assertEqual(expenses[0]['description'], 'Lunch')
        
        # Test today's expenses
        today_expenses = self.storage.get_today_expenses(self.test_user_id, today)
        self.assertEqual(len(today_expenses), 1)
    
    def tearDown(self):
        """Clean up test data"""
        if self.test_user_id in self.storage._users:
            del self.storage._users[self.test_user_id]
        if self.test_user_id in self.storage._tasks:
            del self.storage._tasks[self.test_user_id]
        if self.test_user_id in self.storage._habits:
            del self.storage._habits[self.test_user_id]
        if self.test_user_id in self.storage._expenses:
            del self.storage._expenses[self.test_user_id]
        self.storage._save_all_data()

class TestMediaMerger(unittest.TestCase):
    """Test MediaMerger functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.merger = MediaMerger()
    
    def test_is_video_file(self):
        """Test video file detection"""
        self.assertTrue(self.merger.is_video_file('test.mp4'))
        self.assertTrue(self.merger.is_video_file('video.avi'))
        self.assertTrue(self.merger.is_video_file('movie.mov'))
        self.assertFalse(self.merger.is_video_file('document.pdf'))
        self.assertFalse(self.merger.is_video_file('image.jpg'))
    
    def test_is_pdf_file(self):
        """Test PDF file detection"""
        self.assertTrue(self.merger.is_pdf_file('document.pdf'))
        self.assertTrue(self.merger.is_pdf_file('report.PDF'))
        self.assertFalse(self.merger.is_pdf_file('test.mp4'))
        self.assertFalse(self.merger.is_pdf_file('image.jpg'))
    
    def test_get_file_type(self):
        """Test file type detection"""
        self.assertEqual(self.merger.get_file_type('test.mp4'), 'video')
        self.assertEqual(self.merger.get_file_type('document.pdf'), 'pdf')
        self.assertEqual(self.merger.get_file_type('image.jpg'), 'unknown')

class TestOCREngine(unittest.TestCase):
    """Test OCR Engine functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.ocr_engine = HindiOCREngine()
    
    def test_initialization(self):
        """Test OCR engine initialization"""
        self.assertIsNotNone(self.ocr_engine)
    
    def test_preprocess_image(self):
        """Test image preprocessing functionality"""
        # Create a simple test image
        import cv2
        import numpy as np
        
        img = np.ones((200, 400, 3), dtype=np.uint8) * 255
        img = cv2.putText(img, 'नमस्ते', (50, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Save as temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            cv2.imwrite(f.name, img)
        
        # Test preprocessing
        preprocessed = self.ocr_engine.preprocess_image(f.name)
        self.assertIsNotNone(preprocessed)
        
        # Clean up
        os.remove(f.name)

class TestPDFHandler(unittest.TestCase):
    """Test PDF Handler functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.pdf_handler = PDFHandler()
    
    def test_initialization(self):
        """Test PDF handler initialization"""
        self.assertIsNotNone(self.pdf_handler)

def main():
    """Run all tests"""
    print("🚀 Running RADHEY AI LIFE COMMANDER Tests")
    print("=" * 50)
    
    test_classes = [TestFileStorage, TestMediaMerger, TestOCREngine, TestPDFHandler]
    
    for test_class in test_classes:
        print(f"\n🧪 Testing: {test_class.__name__}")
        print("-" * 30)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
        result = runner.run(suite)
        
        if result.failures:
            print(f"❌ {len(result.failures)} tests failed")
        if result.errors:
            print(f"❌ {len(result.errors)} errors occurred")
        if result.wasSuccessful():
            print(f"✅ All {result.testsRun} tests passed")
        print()
    
    # Run project structure test
    print("📁 Project Structure Test")
    print("=" * 30)
    
    try:
        from test_structure import test_structure
        test_structure()
    except Exception as e:
        print(f"❌ Project structure test failed: {e}")
    
    print()
    
    # Check dependencies
    print("📦 Dependency Check")
    print("=" * 30)
    
    missing_deps = []
    required_deps = [
        'python-telegram-bot', 'python-dateutil', 'Pillow', 'opencv-python',
        'pdfminer.six', 'PyPDF2', 'numpy', 'python-dotenv', 'Werkzeug',
        'requests', 'matplotlib', 'pandas', 'openpyxl', 'SpeechRecognition',
        'pydub'
    ]
    
    for dep in required_deps:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - Not installed")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n❌ {len(missing_deps)} dependencies missing. Please run:")
        print("pip install -r requirements.txt")
    
    return len(missing_deps) == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(1)
