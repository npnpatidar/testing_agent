import os
from dotenv import load_dotenv
import google.generativeai as genai
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Load environment variables from .env file
load_dotenv()

# Get the Gemini API key from the .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please provide a Gemini API key in the .env file.")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def sanitize_filename(filename):
    """Removes invalid characters for filenames."""
    return re.sub(r'[\\/*?"<>|]', '', filename)

def get_transcript(video_id):
    """Fetch transcript in English, fallback to Hindi."""
    try:
        return YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except:
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
        except:
            return None

def save_transcript(folder_name, video_title, transcript):
    """Save transcript to a text file."""
    if transcript:
        os.makedirs(folder_name, exist_ok=True)
        filename = os.path.join(folder_name, sanitize_filename(video_title) + ".txt")
        with open(filename, "w", encoding="utf-8") as f:
            for entry in transcript:
                f.write(entry['text'] + '\n')

def generate_summary(transcript, summary_folder, video_title):
    """Generate a summary of the transcript and save it."""
    if transcript:
        os.makedirs(summary_folder, exist_ok=True)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(
            f"Extract detailed and structured notes from the following lecture transcript. "
            f"Ensure that the notes are concise, to the point, and optimized for exam revision. "
            f"Avoid any promotional, motivational, or unnecessary filler content. "
            f"Focus on key concepts, definitions, formulas, and important takeaways. "
            f"Use markdown format for clarity, including headers, bullet points, tables if needed. "
            f"Do not include opinions or redundant explanations. "
            f"Format the notes in a well-organized manner suitable for effective review.\n\n"
            f"REMEMBER TO CREATE WELL ORGANIZED NOTES AND NOT SUMMARY"
            f"Transcript:\n{transcript}"
        )
        
        summary_filename = os.path.join(summary_folder, sanitize_filename(video_title) + "_summary.md")
        with open(summary_filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Summary saved: {summary_filename}")

def main(video_url):
    ydl_opts = {
        'quiet': True,
        'format': 'best',
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        video_title = sanitize_filename(info.get('title', 'Untitled Video'))
        video_id = info.get('id')
        transcript_folder = "Transcripts"
        summary_folder = "Summaries"
        
        print(f"Processing: {video_title}")
        transcript = get_transcript(video_id)
        if transcript:
            save_transcript(transcript_folder, video_title, transcript)
            generate_summary("\n".join([entry['text'] for entry in transcript]), summary_folder, video_title)
            print(f"Processed: {video_title}")
        else:
            print(f"Transcript not available for: {video_title}")
    
    print("Completed extracting transcript and generating summary.")

if __name__ == "__main__":
    video_url = input("Enter YouTube Video URL: ")
    main(video_url)
