# PROJECT SUMMARY: RADHEY AI LIFE COMMANDER

## OVERVIEW
This project implements a comprehensive AI life commander bot with multiple features to help users manage their daily lives, expenses, tasks, and habits in Hindi language.

## CORE FEATURES IMPLEMENTED

### 1. TASK MANAGEMENT
- **Add Task**: `/addtask` - Add new daily tasks with time detection
- **View Tasks**: `/today`, `/tomorrow`, `/alltasks` - View scheduled tasks
- **Edit Tasks**: `/reschedule`, `/deletetask`, `/clear` - Modify existing tasks
- **Natural Language Parsing**: Convert Hindi time expressions (e.g., "7 baje") to 24h format

### 2. HABIT TRACKING
- **Add Habit**: `/addhabit` - Create new habits with optional descriptions
- **Track Habits**: `/done`, `/habits`, `/streak`, `/report` - Monitor habit completion and streaks
- **Gamification**: XP system for habit completion

### 3. EXPENSE MANAGEMENT
- **Add Expense**: `/addexpense` - Record expenses with auto-category detection
- **View Expenses**: `/todayexpense`, `/weekexpense`, `/monthexpense` - Track spending patterns
- **Reports**: `/weekpdf`, `/budget`, `/topcategory`, `/exportcsv`, `/clearexpense` - Detailed expense reports

### 4. DAILY ROUTINES
- **Morning Routine**: `/morning` - Start the day with tasks and habits
- **Night Planner**: `/night` - Plan tomorrow's schedule interactively
- **Reminders**: `/reminder` - Toggle notifications

### 5. VOICE & OCR
- **Voice Mode**: `/talk` - Enable voice interaction (speech-to-text stub)
- **Hindi OCR**: `/scan` - Extract text from Hindi images (stub)

### 6. ANALYTICS & GAMIFICATION
- **Stats**: `/stats` - View productivity and expense statistics
- **XP System**: `/xp`, `/level` - Track progress with experience points
- **Challenges**: `/challenge` - Daily challenges for motivation

### 7. CALENDAR & DASHBOARD
- **Google Calendar**: `/gcal connect`, `/gcal sync`, `/gcal off` - Sync tasks with Google Calendar
- **Web Dashboard**: `/dashboard` - Web interface for visualizing data

### 8. MEDIA MERGER (NEW)
- **Merge Command**: `/merge` - Merge multiple media files (videos or PDFs) into one
  - **Workflow**:
    1. Send `/merge` command
    2. Bot asks for media files (videos or PDFs)
    3. User sends files one by one
    4. Bot displays media info and asks for confirmation
    5. User selects quality (1.High, 2.Medium, 3.Low)
    6. Bot merges files and sends back the result
  - **Supported Formats**: Videos (MP4, AVI, MOV, MKV, FLV, WMV), PDFs
  - **Quality Options**: High (best quality, largest file), Medium (balanced), Low (fastest, smallest)
  - **Features**: Automatic format detection, validation, and progress tracking

## TECHNICAL ARCHITECTURE

### File Structure
```
Rk_Bot/
├── bot/
│   └── main.py              # Main bot implementation with command handlers
├── core/
│   ├── database.py          # Database management
│   ├── media_merger.py      # Media file merging functionality
│   ├── ocr_engine.py        # OCR engine for text extraction
│   ├── pdf_handler.py       # PDF handling and reporting
│   └── test_generator.py    # Test data generation
├── logs/                     # Bot logs directory
├── tmp/                      # Temporary files storage
├── README.md                 # Project documentation
├── DEPLOYMENT.md             # Deployment instructions
├── DEPLOYMENT_RENDER.md      # Render.com deployment guide
├── PROJECT_SUMMARY.md        # This summary file
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variables template
```

### Dependencies
Key Python libraries used:
- `python-telegram-bot` - Telegram API integration
- `pymongo`, `motor` - MongoDB connection
- `pytesseract`, `opencv-python` - OCR functionality
- `pdfminer.six`, `PyPDF2` - PDF handling
- `numpy`, `scikit-image` - Image processing
- `matplotlib`, `pandas` - Data visualization and analysis
- `speech_recognition`, `pyaudio` - Voice recognition (stub)

### Database Structure
The bot uses MongoDB to store user data:
- **Users**: User profiles, preferences, and stats
- **Tasks**: Scheduled tasks with dates and times
- **Habits**: Habit definitions and tracking
- **Expenses**: Expense records with categories and amounts

## INSTALLATION & RUNNING

### Prerequisites
1. Python 3.8+
2. MongoDB
3. Tesseract OCR
4. FFmpeg (for video merging)

### Installation Steps
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate venv: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure environment variables
6. Run the bot: `python bot/main.py` or use `/start.sh` script

## USAGE EXAMPLES

### Task Management
```
User: /addtask 7 baje gym jana hai
Bot: Ji Radhey ji, 7 baje gym ka reminder set kar diya hai.

User: /today
Bot: 📅 **Aaj ke Task:**
     • [ ] 07:00 AM - Gym jana hai
```

### Habit Tracking
```
User: /addhabit Daily Walk
Bot: Habit 'Daily Walk' added successfully!

User: /done 1
Bot: Daily Walk marked as complete! Current streak: 5 days
```

### Expense Management
```
User: /addexpense 500 rupees petrol
Bot: ₹500 Fuel category me add kar diya Radhey ji. Total expense ₹500.
```

### Media Merging
```
User: /merge
Bot: Radhey ji, please send media files (videos or PDFs) that you want to merge.

User: [sends video1.mp4, video2.mp4]
Bot: 📊 Files to merge:
     • 🎥 video1.mp4 (00:05:30, 100.0 MB)
     • 🎥 video2.mp4 (00:03:45, 80.0 MB)
     
     📈 Total: 2 file(s), 180.00 MB
     ⏱️ Total duration: 00:09:15
     
     📋 If you want to merge these files, type '1' to proceed. Otherwise, type 'cancel'.

User: 1
Bot: 🔍 Please select quality:
     1. High (Best quality, larger file size)
     2. Medium (Good quality, balanced file size)
     3. Low (Fast processing, smaller file size)
```

## DEPLOYMENT OPTIONS

### Local Development
```bash
python bot/main.py
```

### Render.com Deployment
- Follow detailed instructions in `DEPLOYMENT_RENDER.md`
- Deploy to Render.com for free
- Uses Redis for queue management
- Auto-scaling capabilities

## ERROR HANDLING & VALIDATION

The bot includes comprehensive error handling:
- Invalid inputs are rejected with appropriate messages
- Media files are validated before processing
- Merge operations handle file size limits and format checks
- Users can cancel operations at any stage

## TESTING

Test files are provided to verify functionality:
- `test_structure.py` - Tests project structure
- `test_simulation.py` - Simulates bot interactions
- `test_ai_life_commander.py` - Tests core bot functionality
- `test_ocr_engine.py` - Tests OCR engine

## CONTRIBUTIONS

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a new branch
3. Make changes and add tests
4. Submit a pull request

## LICENSE

MIT License

## CONTACT

For support or questions, please contact the development team.
