import os
import re
import subprocess
import logging
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import google.generativeai as genai
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please provide a Gemini API key in the .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# Configure logging
logging.basicConfig(
    filename="process.log", level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def sanitize_filename(filename):
    return re.sub(r'[\\/*?"<>|]', '', filename)

def extract_video_id(video_url):
    parsed_url = urlparse(video_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("v", [None])[0]  # Extract only the video ID

def get_transcript(video_id):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except:
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
        except:
            return None

def download_subtitles(video_url, video_title):
    subtitle_file = f"{video_title}.hi.srt"
    transcript_file = f"Transcripts/{video_title}.txt"
    try:
        command = [
            "yt-dlp", "--write-auto-sub", "--sub-lang", "hi",
            "--skip-download", "--convert-subs", "srt",
            "-o", f"{video_title}.%(ext)s", video_url
        ]
        subprocess.run(command, check=True)
        
        if os.path.exists(subtitle_file):
            clean_command = [
                "sed", "-E",
                's/^[0-9]+$//; s/^[0-9:, -->]+$//; s/^\s+|\s+$//g; /^$/d',
                subtitle_file
            ]
            with open(transcript_file, "w", encoding="utf-8") as f:
                subprocess.run(clean_command, stdout=f, check=True)
            
            os.remove(subtitle_file)
            return transcript_file
    except Exception as e:
        logging.error(f"Error downloading subtitles: {e}")
    return None

def save_transcript(folder_name, video_title, transcript):
    os.makedirs(folder_name, exist_ok=True)
    filename = os.path.join(folder_name, sanitize_filename(video_title) + ".txt")
    with open(filename, "w", encoding="utf-8") as f:
        for entry in transcript:
            f.write(entry['text'] + '\n')
    return filename

def generate_summary(transcript, summary_folder, video_title):
    os.makedirs(summary_folder, exist_ok=True)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(
        f"Extract detailed and structured notes from the following lecture transcript. "
        f"Ensure that the notes are concise, to the point, and optimized for exam revision. "
        f"Avoid any promotional, motivational, or unnecessary filler content. "
        f"Focus on key concepts, definitions, formulas, and important takeaways but DO NOT MISS any important information. "
        f"Use markdown format for clarity, including headers, bullet points, tables,  if needed. "
        f"Do not include opinions or redundant explanations. "
        f"Format the notes in a well-organized manner suitable for effective review.\n\n"
        f"REMEMBER TO CREATE WELL ORGANIZED NOTES AND NOT SUMMARY"
        f"Transcript:\n{transcript}"
    )
    
    summary_filename = os.path.join(summary_folder, sanitize_filename(video_title) + "_summary.md")
    with open(summary_filename, "w", encoding="utf-8") as f:
        f.write(response.text)
    logging.info(f"Summary saved: {summary_filename}")

def main(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        logging.error("Invalid video URL. Unable to extract video ID.")
        print("Invalid video URL. Please enter a valid YouTube video link.")
        return
    
    ydl_opts = {
        'quiet': True,
        'format': 'best',
        'extract_flat': False,
        'force_generic_extractor': False,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        video_title = sanitize_filename(info.get('title', 'Untitled Video'))
        transcript_folder = "Transcripts"
        summary_folder = "Summaries"
        
        logging.info(f"Processing: {video_title}")
        transcript = get_transcript(video_id)
        
        if transcript:
            transcript_file = save_transcript(transcript_folder, video_title, transcript)
        else:
            transcript_file = download_subtitles(video_url, video_title)
        
        if transcript_file:
            with open(transcript_file, "r", encoding="utf-8") as f:
                transcript_text = f.read()
            generate_summary(transcript_text, summary_folder, video_title)
        else:
            logging.warning(f"Transcript not available for: {video_title}")
        
    logging.info("Completed extracting transcript and generating summary.")

if __name__ == "__main__":
    video_url = input("Enter YouTube Video URL: ")
    main(video_url)