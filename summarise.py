import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get the Gemini API key from the .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please provide a Gemini API key in the .env file.")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Load the transcript from transcript.txt
with open("transcript.txt", "r") as file:
    transcript = file.read()

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Generate a summary of the transcript
response = model.generate_content(f"Create very very detailed notes from this lecture. Avoid Promotional and Motivational sections. Notes should be properly structured and should be in english in markdown format. The Notes should not contain opinions, unnecessary and time-wasting things. The Notes should be from the exam point of view and for revision of the subject.   :\n\n{transcript}")

# Save the summary to summary.txt
with open("summary.txt", "w") as file:
    file.write(response.text)

print("Summary saved to summary.txt")
