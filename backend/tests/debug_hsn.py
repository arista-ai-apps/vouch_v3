import os
import json
import base64
import fitz  # PyMuPDF
from openai import OpenAI
import sys

# Hardcoded for debug
OPENAI_API_KEY = "YourAPIKeyHere" # This will fail but I'll use the environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

SYSTEM_PROMPT = """
You are a Senior CA Audit Article. Extract invoice data from the provided OCR text blocks into a structured JSON format.
The OCR text was extracted in 'blocks' format, so some table columns may be grouped. Use your expertise to identify the correct values.
The output MUST be a valid JSON object matching this schema:
{
  "invoice_number": string,
  "hsn_code": string (Identify HSN/SAC codes. They are usually 4, 6, or 8 digits. If multiple, provide as comma-separated.),
  "vendor_name": string,
  "vendor_gstin": string,
}
If a field is not found, use null. HSN/SAC codes are critical—look for them carefully in the items area.
"""

def debug_extract(file_path):
    print(f"DEBUG: Opening {file_path}")
    doc = fitz.open(file_path)
    ocr_text = ""
    for page in doc:
        blocks = page.get_text("blocks")
        for b in blocks:
            ocr_text += f"{b[4]}\n"
    doc.close()
    
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
