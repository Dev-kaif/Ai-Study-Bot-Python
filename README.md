# 📚 AI Study Assistant (Powered by Gemini API)

This Python module helps students generate useful study material from any text content. It uses the **Google Gemini API** to generate:
- ✅ Concise summaries  
- 📇 Flashcards for revision  
- 📝 Multiple-choice quizzes  
- 🧠 Quiz evaluation with score and explanations

---

## ✨ Features

- **Generate Summary**: Clear and concise summaries for better understanding.
- **Create Flashcards**: Converts content into Q/A format flashcards (5–10 cards).
- **Build Quizzes**: Multiple choice quizzes (5 questions) for self-assessment.
- **Evaluate Quizzes**: AI-powered feedback based on user answers.

---

## 🧠 How It Works

This project uses the `gemini-1.5-flash` model from Google's GenAI API. You provide raw content (e.g., textbook passage, notes), and the AI returns study material in the specified format.

---

## 🛠️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-study-assistant.git
   cd ai-study-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file**
   ```
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

4. **Run the script**
   Import and call functions from your main script.

---

## 🧪 Usage Example

```python
from your_module_name import generate_summary, generate_flashcards, generate_quiz, evaluate_quiz

text = "Photosynthesis is the process used by plants to convert light energy into chemical energy..."

summary = generate_summary(text)
print(summary)

flashcards = generate_flashcards(text)
print(flashcards)

quiz = generate_quiz(text)
print(quiz)

user_answers = ["a", "b", "c", "a", "d"]
evaluation = evaluate_quiz(quiz, user_answers)
print(evaluation)
```

---

## 📂 Project Structure

```
📁 ai-study-assistant/
├── 📁 utils/
    ├── ai_utils.py
    ├── input_utils.py
    ├── youtube_utils.py
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## 📦 Requirements

- Python 3.8+
- `google-generativeai`
- `python-dotenv`

Install all dependencies via:

```bash
pip install -r requirements.txt
```

---

## 🌟 Star This Repo

If you found this useful, consider starring the repo 🌟

