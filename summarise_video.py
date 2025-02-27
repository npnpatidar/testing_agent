import os
import subprocess
import requests
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re


# Constants for file paths
PROCESSED_FILE = "processed_videos.txt"
SUMMARY_DIR = "summaries"

# Construct the RSS URL using the channel ID
def get_rss_url(channel_id):
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

# Parse the RSS feed and return video entries
def get_rss_videos(channel_id):
    rss_url = get_rss_url(channel_id)
    feed = feedparser.parse(rss_url)
    return feed.entries

# Read processed video IDs from file
def read_processed_videos():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            processed = {line.strip() for line in f if line.strip()}
    else:
        processed = set()
    return processed

# Append a new video ID to the processed file
def update_processed_file(video_id):
    with open(PROCESSED_FILE, "a") as f:
        f.write(f"{video_id}\n")



def download_transcript(video_url):
    """
    Fetches the transcript for a YouTube video using the youtube_transcript_api.
    Returns the transcript as a single concatenated string.
    """
    video_id = get_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL.")
        return
            
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi','en'])
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return transcript_text        
        
    except Exception as e:
        print("Error fetching transcript:", e)
        return None

# Summarize transcript using Gemini API
def summarize_text(text, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(text)

    
    return response.text

# Save summary to a markdown file
def save_summary(title, summary):
    safe_title = title.replace(" ", "_").replace("/", "_")
    filename = f"{SUMMARY_DIR}/{safe_title}.md"
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(summary)
    return filename

# Commit changes to Git
def commit_changes(files, commit_message):
    subprocess.run(["git", "config", "--global", "user.email", "action@github.com"], check=True)
    subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=True)
    subprocess.run(["git", "add"] + files, check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push"], check=True)

def extract_views(entry):
    """
    Extract the view count from the RSS entry.
    Assumes that entry['media_statistics']['views'] contains the view count as a string.
    """
    try:
        views = int(entry['media_statistics']['views'])
    except (KeyError, ValueError, TypeError):
        views = 0
    return views

def get_video_id(url):
        """Extract video ID from YouTube URL."""
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, url)
        return match.group(1) if match else None

def main():
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    if not channel_id or not gemini_api_key:
        raise Exception("Missing required environment variables.")
    
    # Get the list of videos from the RSS feed
    entries = get_rss_videos(channel_id)
    processed = read_processed_videos()
    
    files_to_commit = []
    
    for entry in entries:
        video_id = entry.yt_videoid  # Provided by feedparser for YouTube feeds
        title = entry.title
        
        # Filter for videos with "Current Affairs" in the title (case-insensitive)
        if "current affairs" not in title.lower():
            continue

        # Skip if already processed
        if video_id in processed:
            continue

        # Extract view count from the RSS entry
        views = extract_views(entry)
        if views == 0:
            print(f"Skipping video '{title}' (ID: {video_id}) because view count is zero.")
            continue

        video_url = entry.link
        print(f"Processing video: {title} (ID: {video_id}) with {views} views")
        
        try:
            transcript = download_transcript(video_url)
            summary = summarize_text(transcript, gemini_api_key)
            summary_file = save_summary(title, summary)
            files_to_commit.append(summary_file)
            
            # Update processed videos file
            update_processed_file(video_id)
            files_to_commit.append(PROCESSED_FILE)
        except Exception as e:
            print(f"Error processing video {video_id}: {e}")
    
    if files_to_commit:
        commit_message = "Add summaries for new Current Affairs videos"
        commit_changes(files_to_commit, commit_message)
    else:
        print("No new videos to process.")

if __name__ == "__main__":
    main()
