from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
import os
import re

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

def save_transcript(video_title, transcript):
    """Save transcript to a text file."""
    if transcript:
        filename = sanitize_filename(video_title) + ".txt"
        with open(filename, "w", encoding="utf-8") as f:
            for entry in transcript:
                f.write(entry['text'] + '\n')

def main(playlist_url):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        playlist_title = playlist_info.get('title', 'Untitled Playlist')
        print(f"Fetching transcripts for playlist: {playlist_title}")
        
        for entry in playlist_info['entries']:
            video_title = entry.get('title', 'Untitled Video')
            video_id = entry.get('id')
            print(f"Processing: {video_title}")
            transcript = get_transcript(video_id)
            if transcript:
                save_transcript(video_title, transcript)
                print(f"Saved: {video_title}.txt")
            else:
                print(f"Transcript not available for: {video_title}")
    
    print("Completed extracting transcripts.")

if __name__ == "__main__":
    playlist_url = input("Enter YouTube Playlist URL: ")
    main(playlist_url)
