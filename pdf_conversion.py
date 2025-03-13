import pdf2image
import g4f
from PIL import Image
import io
import base64


pdf_path = input("give the path:   ")
#pdf_path = "/home/naresh/Desktop/HISTORY BOOKLET 2024-25-002.pdf"
extracted_path = pdf_path.replace('.pdf','.md')
text = ''

def extract_text_from_image(image_path):
    try:
        # Read the image file
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

        # Convert image data to PIL Image object
        image = Image.open(io.BytesIO(image_data))

        # Convert PIL Image object to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Encode the image to base64
        encoded_image = base64.b64encode(img_byte_arr).decode('utf-8')

        # Call Gemini to extract text from the image
        response = g4f.ChatCompletion.create(
            base_url="http://alma:1337",
            model=g4f.models.gpt_4o_mini,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f'data:image/png;base64,{encoded_image}'
                        }
                    },
                    {
                        "type": "text",
                        "text": "Extract the text from this image. Do not make any commentary whatsoever. Response should be EXTRACTED TEXT ONLY"
                    }
                ]
            }]
        )
        extracted_text = response
        return extracted_text
    except Exception as e:
        return f"Error during text extraction: {e}"


try:
    images = pdf2image.convert_from_path(pdf_path)
    for i, image in enumerate(images):
        image_path = f'/tmp/page_{i}.png'
        image.save(image_path, 'PNG')
        print(f'Extracting text from page {i+1}...')
        extracted_text = extract_text_from_image(image_path)
        print(f'Page {i+1} Text:\n\n {extracted_text}')
        text += f'Page {i+1}: {extracted_text}\n'

    print(f'Extracted text: {text}')
    with open(extracted_path, 'w') as f:
        f.write(text)
    print(f'Extracted text saved to: {extracted_path}')
except Exception as e:
    print(f'Error processing PDF: {e}')
