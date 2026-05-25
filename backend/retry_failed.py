import sys
import os
import asyncio
import time

# Current script is in backend/retry_failed.py
# Parent is backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.files import process_uploaded_file
from app.core.database import SessionLocal
from app.models import models

async def retry_all():
    db = SessionLocal()
    try:
        # Fetch all failed files
        failed_files = db.query(models.UploadedFile).filter(models.UploadedFile.status == "failed").all()
        print(f"[RETRY] Found {len(failed_files)} failed files.")
        
        for file_row in failed_files:
            print(f"[RETRY] Attempting to process: {file_row.filename} (ID: {file_row.id})")
            
            # Clear any partial extraction records for a clean retry
            db.query(models.ExtractedInvoice).filter(models.ExtractedInvoice.file_id == file_row.id).delete()
            db.commit()
            
            try:
                # Run the background processor synchronously in this loop
                await process_uploaded_file(file_row.id)
                # Sleep to avoid OpenAI rate limits (Tier 1/Free limits are often low)
                print("[RETRY] Sleeping for 10 seconds to respect rate limits...")
                await asyncio.sleep(10)
            except Exception as e:
                print(f"[RETRY] Internal error for file {file_row.id}: {e}")
                continue
            
        print("[RETRY] Finished processing all failed files.")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(retry_all())
