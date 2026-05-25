import sys
import os
import json
import fitz

# Setup path so we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from app.core.config import settings
from app.services.extraction import get_pdf_ocr_text, SYSTEM_PROMPT
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def debug_extract(file_path):
    print(f"DEBUG: Extracting text from {file_path}")
    ocr_text = get_pdf_ocr_text(file_path)
    
    print("DEBUG: OCR TEXT EXTRACTED:")
    print("-" * 20)
    print(ocr_text)
    print("-" * 20)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract details from this invoice OCR text:\n\n{ocr_text}"},
        ],
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    print("DEBUG: AI JSON RESPONSE:")
    print(content)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_extract(sys.argv[1])
    else:
        print("Usage: python debug_hsn.py <pdf_path>")
