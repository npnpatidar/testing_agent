from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_video_id(url):
        """Extract video ID from YouTube URL."""
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, url)
        return match.group(1) if match else None

def fetch_transcript(video_url):
    """Fetch and save the transcript of a YouTube video."""
    video_id = get_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL.")
        return
            
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi','en'])
        transcript_text = "\n".join([entry['text'] for entry in transcript])
                
        with open("transcript.txt", "w", encoding="utf-8") as file:
            file.write(transcript_text)
                    
            print("Transcript saved to transcript.txt")
    except Exception as e:
        print("Error fetching transcript:", e)

if __name__ == "__main__":
    url = input("Enter YouTube URL: ")
    fetch_transcript(url)


