from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini client setup
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_youtube_transcript(video_url):
    try:
        video_id = extract_video_id(video_url)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try English first
        try:
            transcript = transcript_list.find_transcript(['en'])
            transcript_text = " ".join([t.text for t in transcript.fetch()])
            return transcript_text

        except NoTranscriptFound:
            # Try Hindi as fallback
            try:
                transcript = transcript_list.find_transcript(['hi'])
                hindi_text = " ".join([t.text for t in transcript.fetch()])
                translated_text = translate_hindi_to_english(hindi_text)
                return translated_text
            except NoTranscriptFound:
                return "No transcript found in English or Hindi."

    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def translate_hindi_to_english(hindi_text: str) -> str:
    prompt = f"""
Translate the following Hindi transcript to English. Do not add any explanations or headings.

Hindi Transcript:
{hindi_text}
"""
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Translation error: {e}"
