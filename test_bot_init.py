#!/usr/bin/env python3
"""
Test script to verify bot initialization without Telegram connection
"""

import sys
import os

def test_bot_import():
    """Test if bot module can be imported"""
    try:
        from bot.main import RadheyAIBot
        print("✅ Bot module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import bot module: {e}")
        return False

def test_file_storage():
    """Test FileStorage functionality"""
    try:
        from core.file_storage import get_file_storage
        storage = get_file_storage()
        print("✅ FileStorage initialized")
        
        # Test user creation
        user_id = 55555
        storage.save_user(user_id, 'testuser', 'Test', 'User', 98765)
        user = storage.get_user(user_id)
        print(f"✅ User created: {user}")
        
        # Test task creation
        today = storage._today_str()
        storage.add_task(user_id, 'Test task', today, '10:00')
        tasks = storage.get_user_tasks(user_id)
        print(f"✅ Tasks: {len(tasks)}")
        
        # Cleanup
        if user_id in storage._users:
            del storage._users[user_id]
        if user_id in storage._tasks:
            del storage._tasks[user_id]
        storage._save_all_data()
        
        print("✅ FileStorage test passed")
        return True
        
    except Exception as e:
        print(f"❌ FileStorage test failed: {e}")
        return False

def test_media_merger():
    """Test MediaMerger functionality"""
    try:
        from core.media_merger import MediaMerger
        merger = MediaMerger()
        print("✅ MediaMerger initialized")
        
        # Test file type detection
        video_test = merger.is_video_file('test.mp4')
        pdf_test = merger.is_pdf_file('document.pdf')
        print(f"✅ Video detection: {video_test}")
        print(f"✅ PDF detection: {pdf_test}")
        
        return True
    except Exception as e:
        print(f"❌ MediaMerger test failed: {e}")
        return False

def test_ocr_engine():
    """Test OCR engine functionality"""
    try:
        from core.ocr_engine import HindiOCREngine
        ocr_engine = HindiOCREngine()
        print("✅ OCR engine initialized")
        return True
    except Exception as e:
        print(f"❌ OCR engine test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🚀 Testing RADHEY AI LIFE COMMANDER")
    print("=" * 50)
    
    tests = [
        test_bot_import,
        test_file_storage,
        test_media_merger,
        test_ocr_engine
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print()
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
            failed += 1
    
    print()
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All basic tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
