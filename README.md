# RADHEY AI LIFE OS (Hindi OCR Optimized Version) 🚀

## 📋 Project Overview

A production-ready Telegram AI SaaS Bot with high accuracy Hindi OCR engine, MCQ detection, and interactive quiz generation capabilities. Built for students, educators, and professionals working with Hindi language materials.

## ✨ Key Features

### 📄 **Hindi OCR Engine**
- **High Accuracy Hindi OCR**: Powered by Tesseract with `hin.traineddata` language pack
- **PDF & Image Support**: Handles both text-based and scanned PDFs, JPG, PNG images
- **Advanced Preprocessing**: OpenCV-based image enhancement for better OCR results
- **Unicode Normalization**: Fixes broken characters and matras in extracted text
- **PDF Type Detection**: Automatically distinguishes between text-based and scanned PDFs

### 📝 **MCQ Detection Logic**
- **Pattern Recognition**: Detects Hindi/English question patterns like:
  - प्रश्न 1. / Q.1 / (1)
  - Options: A), (क), (ख), (ग), etc.
- **Structured Extraction**: Outputs JSON with question numbers, text, options, and correct answers
- **Hindi Numbering Support**: Handles Devanagari numerals and mixed Hindi-English content
- **Paragraph Questions**: Supports multi-line question extraction

### 🎯 **Test Generator**
- **Clean Unicode HTML**: Responsive quiz interface with Noto Sans Devanagari font
- **Timer-Based Quiz**: Configurable time limits per quiz
- **Auto Scoring**: Real-time results with detailed explanations
- **Leaderboard**: Track quiz performance and compare with others
- **Mobile Optimized**: Works seamlessly on all device sizes

### 🚀 **Advanced Features**
- **Kruti Dev Font Detection**: Attempts to convert legacy font encoding to Unicode
- **Low Confidence Handling**: Offers to enhance and retry OCR for poor quality images
- **Export Options**: JSON, TXT, HTML (with CSS), and ZIP downloads
- **Async Processing**: Background task queue for large file handling
- **Database Storage**: File-based storage (JSON files) for tracking user results

## 🏗️ Architecture

```
RADHEY AI BOT
├── Telegram Bot Interface (python-telegram-bot)
├── OCR Engine (Tesseract + OpenCV)
│   ├── Image Preprocessing
│   ├── Hindi Text Extraction
│   └── Unicode Normalization
├── PDF Handler (PyMuPDF + pdf2image)
│   ├── Text-based PDF Extraction
│   └── Scanned PDF to Image Conversion
├── MCQ Detector (Regex + NLP)
│   ├── Question Detection
│   ├── Option Extraction
│   └── Answer Detection
├── Test Generator (HTML/CSS/JS)
│   ├── Quiz Rendering
│   ├── Timer Logic
│   └── Scoring System
└── Database (MongoDB)
    ├── User Management
    ├── OCR Results Storage
    └── Quiz Statistics
```

## 🛠️ Technology Stack

- **Python 3.9+**: Core backend language
- **Tesseract OCR**: Hindi language processing
- **OpenCV**: Image preprocessing and enhancement
- **PyMuPDF & pdf2image**: PDF handling and conversion
- **python-telegram-bot**: Telegram bot integration
- **MongoDB**: Database for storage and analytics
- **Flask**: Web server (for webhook support)
- **Celery + Redis**: Async task processing (optional)
- **HTML/CSS/JavaScript**: Quiz interface

## 📦 Installation

### Prerequisites

1. **Python 3.9+** installed
2. **Tesseract OCR** with Hindi language pack
3. **MongoDB** (local or cloud instance)
4. **Git** for version control

### Quick Start

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd radhey_ai
   ```

2. **Run Startup Script**
   ```bash
   chmod +x start.sh
   ./start.sh install
   ```

3. **Configure Environment Variables**
   ```bash
   nano .env
   # Fill in your credentials
   ```

4. **Run the Bot**
   ```bash
   ./start.sh run  # Development mode
   # OR
   ./start.sh start  # Background mode
   ```

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot/main.py
```

### Production Deployment

For production environments, refer to [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- Systemd service configuration
- Docker containerization
- Render.com deployment
- Performance optimization
- Monitoring and logging

## 📖 Usage

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and bot introduction |
| `/help` | Show all available commands |
| `/extract` | Extract text and generate MCQ quiz |
| `/ocr` | Perform OCR without MCQ generation |
| `/test` | Take a quiz from your extracted questions |
| `/stats` | View your extraction and quiz statistics |
| `/leaderboard` | View top performers' leaderboard |
| `/cancel` | Cancel current operation |

### Example Workflow

1. **Send File**: Upload a Hindi PDF or photo containing text
2. **Processing**: Bot analyzes and extracts content
3. **Results**: Receive extracted text and detected MCQs
4. **Quiz**: Take interactive quiz from extracted questions
5. **Analytics**: View your performance statistics

## 🎯 Performance Metrics

- **OCR Speed**: ~10-30 seconds per page (depending on image quality)
- **Accuracy**: ~95% for clear Hindi text at 300 DPI
- **Scalability**: Handles multiple concurrent requests with async processing
- **Storage**: MongoDB with efficient document storage

## 📊 Database Schema

### OCR Results Collection
```json
{
  "user_id": 123456789,
  "file_name": "math-paper.pdf",
  "extracted_text": "प्रश्न 1. ...",
  "structured_questions": [
    {
      "question_number": "1",
      "question_text": "यदि x = 2 है तो x² का मान क्या है?",
      "options": ["4", "8", "16", "2"],
      "correct_answer": "A"
    }
  ],
  "date": "2024-01-01T12:00:00",
  "ocr_confidence_score": 89.5
}
```

## 🔧 Configuration

### Environment Variables

```env
TELEGRAM_BOT_TOKEN=your-bot-token-here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=radhey_ai_db
TESSERACT_PATH=/usr/bin/tesseract
PORT=8443
WEBHOOK_URL=your-webhook-url-here
DEBUG=True
```

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract not found**: Check installation and TESSERACT_PATH
2. **Hindi language pack missing**: Install `tesseract-ocr-hin` package
3. **Low OCR accuracy**: Ensure good image quality (300 DPI minimum)
4. **Memory issues**: Reduce DPI or optimize image processing

### Logs

```bash
# Development mode (terminal output)
./start.sh logs

# Background mode (log file)
tail -f logs/bot.log
```

## 📈 Contributing

We welcome contributions to improve the bot! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details

## 🤝 Support

- **GitHub Issues**: Report bugs or feature requests
- **Telegram Group**: Join [@radheyaiteam](https://t.me/radheyaiteam) for support
- **Documentation**: Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guides

## 🚀 Roadmap

- [ ] Advanced NLP-based MCQ extraction
- [ ] Support for more Indian languages
- [ ] ML-based OCR error correction
- [ ] Integration with e-learning platforms
- [ ] API for external integrations

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for Hindi OCR capabilities
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for Telegram API
- Google Fonts for [Noto Sans Devanagari](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari)

---

**Built with ❤️ for Hindi Language Education**
