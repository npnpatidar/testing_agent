import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

def main():
    # Load environment variables
    load_dotenv()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-8b')

    # Read transcript
    with open('transcript.txt', 'r', encoding='utf-8') as file:
        transcript = file.read()

    # Create 500-character chunks
    chunk_size = 9000
    chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]

    comprehensive_notes = []
    previous_notes_summary = ""

    for i in range(len(chunks)):
        # Get context chunks
        prev_chunk = chunks[i-1] if i > 0 else ""
        current_chunk = chunks[i]
        next_chunk = chunks[i+1] if i < len(chunks)-1 else ""

        # Create prompt
        prompt = f"""Create detailed, factual notes for the CURRENT TRANSCRIPT PART below, maintaining continuity 
        with previous notes. Avoid promotional/motivational content. Focus on factual information and key points. Do not provide any extra summary or anything which breaks the continuity while concatenating the notes.Notes should be properly structured and formatted. When concatenating the notes of all the chunks, they should look continous and cohesive.

        PREVIOUS CONTEXT (for reference):
        {prev_chunk}

        CURRENT TRANSCRIPT PART (focus on this):
        {current_chunk}

        NEXT CONTEXT (for reference):
        {next_chunk}

        PREVIOUS NOTES SUMMARY:
        {previous_notes_summary}

        DETAILED NOTES FOR CURRENT PART:"""

        # Generate notes
        response = model.generate_content(prompt)
        current_notes = response.text.strip()

        # Update tracking variables
        comprehensive_notes.append(current_notes)
        previous_notes_summary = "\n".join(comprehensive_notes[-3:])  # Keep last 3 notes for context
        print(previous_notes_summary)

        time.sleep(4)

    # Save comprehensive notes
    with open('notes.txt', 'w', encoding='utf-8') as file:
        file.write("\n\n".join(comprehensive_notes))

if __name__ == "__main__":
    main()
