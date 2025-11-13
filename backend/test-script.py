import google.generativeai as genai
from google.genai import types
import os

# Configure API key (set via env or directly)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# For uploaded image (contents: bytes, mime_type: str e.g., 'image/jpeg')
model = genai.GenerativeModel('gemini-2.5-flash')

prompt = "Extract all text from this image accurately, including any chat messages or dialogue. Output as plain text."

response = model.generate_content(
    [types.Part.from_bytes(data=contents, mime_type=mime_type), prompt]
)

# Get extracted text
extracted_text = response.text.strip()
print(extracted_text)  # Or return/use as needed

# Optional: Handle errors simply
if not extracted_text:
    extracted_text = "No text detected in image."