from google import genai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set up Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_summary(content: str) -> str:
    prompt = f"""
Summarize the following content clearly and concisely for a student:

{content}
"""
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text.strip()


def generate_flashcards(content: str) -> str:
    prompt = f"""
You are a helpful AI assistant.

Generate 5–10 flashcards from the content below in the **EXACT** format:

Q: [question]
A: [short answer]

Do NOT add any extra text like explanations, titles, numbering, or headings. Just output the flashcards in raw format.

Content:
{content}
"""
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text.strip()


def generate_quiz(content: str) -> str:
    prompt = f"""
You are an AI Quiz Generator.

Create a 5-question multiple choice quiz based on the following content.

Format STRICTLY as follows (no answers or explanations):

1. [Question]
a) Option A
b) Option B
c) Option C
d) Option D

Repeat for all 5 questions. Do not include answers, titles, or extra text. Make sure the options are clear.

Content:
{content}
"""
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text.strip()

def evaluate_quiz(quiz_text: str, user_answers: list[str]) -> str:
    prompt = f"""Evaluate this quiz attempt:
Quiz:
{quiz_text}

User's Answers:
{user_answers}

Return the score out of total and mention correct answers and explanations."""
    
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text.strip()
