import os
import json
import zipfile
from datetime import datetime

class TestGenerator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    
    def generate_html_quiz(self, questions, filename="quiz.html", timer=60):
        """Generate Hindi optimized HTML quiz with timer"""
        html_template = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>हिंदी क्विज़</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans Devanagari', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            direction: ltr;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .timer {
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .quiz-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .question {
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }
        
        .question-number {
            font-size: 1.2em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .question-text {
            font-size: 1.1em;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        
        .options {
            display: grid;
            gap: 10px;
        }
        
        .option {
            background: white;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1em;
        }
        
        .option:hover {
            border-color: #667eea;
            background: #f0f4ff;
            transform: translateX(5px);
        }
        
        .option.selected {
            border-color: #667eea;
            background: #e8f0fe;
            font-weight: 500;
        }
        
        .option.correct {
            border-color: #28a745;
            background: #d4edda;
        }
        
        .option.incorrect {
            border-color: #dc3545;
            background: #f8d7da;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            border-radius: 50px;
            cursor: pointer;
            width: 100%;
            font-weight: 700;
            transition: all 0.3s ease;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .results {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .score {
            font-size: 3em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .percentage {
            font-size: 1.5em;
            color: #666;
            margin-bottom: 20px;
        }
        
        .result-message {
            font-size: 1.2em;
            color: #333;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .question-review {
            text-align: left;
            margin-top: 30px;
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
        }
        
        .review-question {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            
            .timer {
                font-size: 1.2em;
                padding: 8px 16px;
            }
            
            .quiz-container, .results {
                padding: 20px;
            }
            
            .question {
                padding: 15px;
            }
            
            .question-text {
                font-size: 1em;
            }
            
            .option {
                padding: 12px;
                font-size: 0.95em;
            }
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        
        .progress {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 हिंदी क्विज़</h1>
            <div class="timer" id="timer">⏱️ 00:00</div>
        </div>
        
        <div class="quiz-container">
            <div class="progress-bar">
                <div class="progress" id="progress" style="width: 0%"></div>
            </div>
            <div id="quiz-content">
                <!-- Questions will be dynamically inserted here -->
            </div>
            <button class="submit-btn" id="submit-btn" onclick="submitQuiz()">सबमिट</button>
        </div>
        
        <div class="results" id="results">
            <h2>🎉 परिणाम</h2>
            <div class="score" id="score">0</div>
            <div class="percentage" id="percentage">0%</div>
            <div class="result-message" id="result-message"></div>
            
            <div class="question-review" id="question-review">
                <h3>📝 प्रश्नों की समीक्षा</h3>
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by RADHEY AI LIFE OS | हिंदी OCR Optimized Version</p>
        </div>
    </div>
    
    <script>
        const questions = {questions_json};
        const timerSeconds = {timer};
        let currentTime = timerSeconds;
        let timerInterval;
        let userAnswers = {};
        let isSubmitted = false;
        
        function startTimer() {
            timerInterval = setInterval(() => {
                currentTime--;
                const minutes = Math.floor(currentTime / 60).toString().padStart(2, '0');
                const seconds = (currentTime % 60).toString().padStart(2, '0');
                document.getElementById('timer').textContent = `⏱️ ${minutes}:${seconds}`;
                
                if (currentTime <= 0) {
                    clearInterval(timerInterval);
                    submitQuiz();
                }
            }, 1000);
        }
        
        function renderQuestions() {
            const quizContent = document.getElementById('quiz-content');
            questions.forEach((q, index) => {
                const questionDiv = document.createElement('div');
                questionDiv.className = 'question';
                questionDiv.innerHTML = `
                    <div class="question-number">प्रश्न ${index + 1}:</div>
                    <div class="question-text">${q.question_text}</div>
                    <div class="options">
                        ${q.options.map((opt, optIndex) => `
                            <div class="option" onclick="selectOption(${index}, ${optIndex})" data-question="${index}" data-option="${optIndex}">
                                ${String.fromCharCode(65 + optIndex)}) ${opt}
                            </div>
                        `).join('')}
                    </div>
                `;
                quizContent.appendChild(questionDiv);
            });
        }
        
        function selectOption(questionIndex, optionIndex) {
            if (isSubmitted) return;
            
            userAnswers[questionIndex] = optionIndex;
            
            // Remove selected class from all options of this question
            const options = document.querySelectorAll(`[data-question="${questionIndex}"]`);
            options.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to the chosen option
            const selectedOption = document.querySelector(`[data-question="${questionIndex}"][data-option="${optionIndex}"]`);
            selectedOption.classList.add('selected');
            
            updateProgress();
        }
        
        function updateProgress() {
            const answered = Object.keys(userAnswers).length;
            const total = questions.length;
            const progress = (answered / total) * 100;
            document.getElementById('progress').style.width = progress + '%';
        }
        
        function calculateScore() {
            let score = 0;
            
            questions.forEach((q, index) => {
                if (userAnswers[index] !== undefined) {
                    // Check if answer is correct (assuming 'correct_answer' is in format A, B, C, D)
                    if (q.correct_answer) {
                        const correctIndex = q.correct_answer.charCodeAt(0) - 65;
                        if (userAnswers[index] === correctIndex) {
                            score++;
                        }
                    }
                }
            });
            
            return {
                score: score,
                total: questions.length,
                percentage: Math.round((score / questions.length) * 100)
            };
        }
        
        function submitQuiz() {
            if (isSubmitted) return;
            
            isSubmitted = true;
            clearInterval(timerInterval);
            
            const result = calculateScore();
            displayResults(result);
        }
        
        function displayResults(result) {
            // Show correct answers
            questions.forEach((q, index) => {
                if (q.correct_answer) {
                    const correctIndex = q.correct_answer.charCodeAt(0) - 65;
                    const correctOption = document.querySelector(`[data-question="${index}"][data-option="${correctIndex}"]`);
                    if (correctOption) {
                        correctOption.classList.add('correct');
                    }
                    
                    // Mark incorrect answers
                    if (userAnswers[index] !== undefined && userAnswers[index] !== correctIndex) {
                        const userOption = document.querySelector(`[data-question="${index}"][data-option="${userAnswers[index]}"]`);
                        if (userOption) {
                            userOption.classList.add('incorrect');
                        }
                    }
                }
            });
            
            // Show results
            document.querySelector('.quiz-container').style.display = 'none';
            const resultsDiv = document.getElementById('results');
            resultsDiv.classList.add('show');
            
            document.getElementById('score').textContent = `${result.score}/${result.total}`;
            document.getElementById('percentage').textContent = `${result.percentage}%`;
            
            let message = '';
            if (result.percentage >= 90) {
                message = '🎉 वाह! बहुत अच्छा किया! आप एक प्रतिभाशाली छात्र हैं!';
            } else if (result.percentage >= 70) {
                message = '👏 अच्छा प्रदर्शन! कुछ और प्रयास से आप एकदम परफेक्ट हो जाएंगे!';
            } else if (result.percentage >= 50) {
                message = '👍 ठीक है! थोड़ा और अभ्यास करें, आप बेहतर कर सकते हैं!';
            } else {
                message = '📖 नerver mind! निरंतर प्रयास करें, सफलता आपके पास है!';
            }
            document.getElementById('result-message').textContent = message;
            
            // Render question review
            const reviewDiv = document.getElementById('question-review');
            questions.forEach((q, index) => {
                const reviewQuestion = document.createElement('div');
                reviewQuestion.className = 'review-question';
                
                const userAnswer = userAnswers[index];
                const userAnswerText = userAnswer !== undefined ? String.fromCharCode(65 + userAnswer) : 'अनुत्तरित';
                const correctAnswerText = q.correct_answer || 'निर्धारित नहीं';
                
                reviewQuestion.innerHTML = `
                    <strong>प्रश्न ${index + 1}:</strong> ${q.question_text}
                    <br>
                    <small>
                        आपका उत्तर: ${userAnswerText} | 
                        सही उत्तर: ${correctAnswerText}
                    </small>
                `;
                reviewDiv.appendChild(reviewQuestion);
            });
        }
        
        // Initialize quiz
        document.addEventListener('DOMContentLoaded', () => {
            renderQuestions();
            startTimer();
        });
    </script>
</body>
</html>
"""
        
        questions_json = json.dumps(questions, ensure_ascii=False, indent=2)
        html_content = html_template.replace('{questions_json}', questions_json).replace('{timer}', str(timer))
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def generate_json_export(self, questions, filename="questions.json"):
        """Generate JSON export of questions"""
        data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_questions': len(questions),
                'language': 'Hindi'
            },
            'questions': questions
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def generate_txt_export(self, questions, filename="questions.txt"):
        """Generate plain text export of questions"""
        lines = []
        lines.append(f"RADHEY AI LIFE OS - Hindi OCR Quiz Export")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Questions: {len(questions)}")
        lines.append("=" * 50)
        lines.append("")
        
        for i, q in enumerate(questions):
            lines.append(f"प्रश्न {i+1}: {q['question_text']}")
            for j, opt in enumerate(q['options']):
                lines.append(f"  {chr(65+j)}) {opt}")
            if q.get('correct_answer'):
                lines.append(f"  ✔️ सही उत्तर: {q['correct_answer']}")
            lines.append("")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return filename
    
    def generate_zip_export(self, questions, base_filename="quiz_export"):
        """Generate ZIP file with all export formats"""
        temp_dir = os.path.dirname(base_filename)
        if temp_dir and not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        zip_path = f"{base_filename}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # JSON export
            json_file = self.generate_json_export(questions, f"{base_filename}.json")
            zipf.write(json_file, os.path.basename(json_file))
            os.remove(json_file)
            
            # TXT export
            txt_file = self.generate_txt_export(questions, f"{base_filename}.txt")
            zipf.write(txt_file, os.path.basename(txt_file))
            os.remove(txt_file)
            
            # HTML quiz
            html_file = self.generate_html_quiz(questions, f"{base_filename}.html")
            zipf.write(html_file, os.path.basename(html_file))
            os.remove(html_file)
        
        return zip_path
