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
response = model.generate_content(f"Create detailed notes from this lecture. Avoid Promotional and Motivational sections. Notes should be in properly structured and should be in english in markdown format. If something can't be asked in exam then avoid and if it can be asked then include.   :\n\n{transcript}")

# Save the summary to summary.txt
with open("summary.txt", "w") as file:
    file.write(response.text)

print("Summary saved to summary.txt")
