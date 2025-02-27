import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

from icecream import ic

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
    chunk_size = 2000
    chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]

    comprehensive_notes = []
    previous_notes_summary = ""

    for i in range(len(chunks)):
        # Get context chunks
        prev_chunk = chunks[i-1] if i > 0 else ""
        current_chunk = chunks[i]
        next_chunk = chunks[i+1] if i < len(chunks)-1 else ""

        # Create prompt
        prompt = f"""
        Create detailed, factual notes for the ONLY CURRENT TRANSCRIPT PART provided below. Ensure the notes maintain continuity with previous notes, avoiding repetition of content already covered. Adhere to the following guidelines:

    Focus on Factual Information: Include only key points, data, and factual details relevant to the current transcript part. Avoid speculative, promotional, or motivational content.

    Maintain Continuity: Ensure the notes seamlessly connect with previous notes, creating a cohesive and continuous flow when concatenated. Do not include summaries, conclusions, or any content that disrupts the continuity.

    Structured Formatting: Organize the notes in a clear, structured format (e.g., bullet points, numbered lists, or paragraphs) for easy readability and logical flow.

    Avoid Redundancy: Do not repeat information already covered in previous notes. Only include new or supplementary details from the current transcript part.

    Precision and Conciseness: Be concise while retaining all critical information. Avoid unnecessary elaboration or filler content.

    Contextual Awareness: Ensure the notes align with the context and tone of the ongoing discussion or transcript, maintaining a consistent narrative.

By following these guidelines, the notes should integrate seamlessly with previous sections, forming a coherent and comprehensive record when combined.


        PREVIOUS CONTEXT (for reference):
        {prev_chunk}

        CURRENT TRANSCRIPT PART (focus on this):
        {current_chunk}

        NEXT CONTEXT (for reference):
        {next_chunk}

        PREVIOUS NOTES SUMMARY(to avoid Redundancy and ensure continuation):
        {previous_notes_summary}

        DETAILED NOTES FOR CURRENT PART:"""

        # Generate notes
        response = model.generate_content(prompt)
        current_notes = response.text.strip()
        ic(current_notes)

        # Update tracking variables
        comprehensive_notes.append(current_notes)
        previous_notes_summary = "\n".join(comprehensive_notes[-3:])  # Keep last 3 notes for context

        time.sleep(4)

    # Save comprehensive notes
    with open('notes.txt', 'w', encoding='utf-8') as file:
        file.write("\n\n".join(comprehensive_notes))

if __name__ == "__main__":
    main()
