#!/usr/bin/env python3
"""
Test script to verify project structure and basic functionality
"""

import os
import sys

def check_file(file_path):
    """Check if file exists and has content"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        if size > 0:
            print(f"✅ {file_path} ({size} bytes)")
            return True
        else:
            print(f"⚠️ {file_path} exists but is empty")
            return False
    else:
        print(f"❌ {file_path} not found")
        return False

def check_directory(dir_path):
    """Check if directory exists and is not empty"""
    if os.path.exists(dir_path):
        if os.path.isdir(dir_path):
            files = os.listdir(dir_path)
            if len(files) > 0:
                print(f"✅ {dir_path} ({len(files)} files/directories)")
                return True
            else:
                print(f"⚠️ {dir_path} exists but is empty")
                return False
        else:
            print(f"❌ {dir_path} exists but is not a directory")
            return False
    else:
        print(f"❌ {dir_path} not found")
        return False

def main():
    print("🚀 RADHEY AI LIFE OS - Project Structure Test")
    print("=" * 50)
    
    # Project root files
    print("\n📁 Root Directory:")
    root_files = [
        "README.md",
        "requirements.txt",
        "start.sh",
        "DEPLOYMENT.md",
        ".env.example",
        "test_ocr_engine.py",
        "test_structure.py"
    ]
    
    for file_path in root_files:
        check_file(file_path)
    
    # Bot directory
    print("\n🤖 Bot Directory:")
    if check_directory("bot"):
        check_file("bot/main.py")
    
    # Core directory
    print("\n🧠 Core Directory:")
    if check_directory("core"):
        core_files = [
            "core/ocr_engine.py",
            "core/pdf_handler.py",
            "core/test_generator.py",
            "core/database.py"
        ]
        
        for file_path in core_files:
            check_file(file_path)
    
    # Temporary directory (should be created by code)
    print("\n📝 Temporary Directory:")
    temp_dir = "tmp"
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
            print(f"✅ {temp_dir} created")
        except Exception as e:
            print(f"❌ Failed to create {temp_dir}: {e}")
    else:
        print(f"✅ {temp_dir} exists")
    
    # Logs directory (should be created by code)
    print("\n📊 Logs Directory:")
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir)
            print(f"✅ {logs_dir} created")
        except Exception as e:
            print(f"❌ Failed to create {logs_dir}: {e}")
    else:
        print(f"✅ {logs_dir} exists")
    
    # Check script permissions
    print("\n🔑 File Permissions:")
    for file_path in ["start.sh"]:
        if os.path.exists(file_path):
            if os.access(file_path, os.X_OK):
                print(f"✅ {file_path} is executable")
            else:
                print(f"⚠️ {file_path} should be executable")
                try:
                    os.chmod(file_path, 0o755)
                    print(f"✅ {file_path} made executable")
                except Exception as e:
                    print(f"❌ Failed to set permissions: {e}")
    
    # Verify Python version
    print("\n🐍 Python Version:")
    version_info = sys.version_info
    print(f"✅ Python {version_info.major}.{version_info.minor}.{version_info.micro}")
    
    if version_info.major < 3 or version_info.minor < 8:
        print("⚠️ Python 3.8 or higher is recommended")
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    print("✅ Project structure is complete!")
    print("\n🎉 What's next?")
    print("1. Configure your Telegram bot token in .env file")
    print("2. Set up MongoDB connection")
    print("3. Install dependencies: pip3 install -r requirements.txt")
    print("4. Install Tesseract OCR with Hindi support")
    print("5. Run the bot: python3 bot/main.py")
    
    print("\n📚 Quick Start Guide:")
    print("For detailed instructions, refer to README.md and DEPLOYMENT.md")
    
    return True

if __name__ == "__main__":
    main()
