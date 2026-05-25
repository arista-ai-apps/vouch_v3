import sys
import os

# Add the parent of the backend directory so we can import app as app
# Current file is in d:\Arista\accontantAI\vouching\backend\sync_reconciliation.py
# So we need to add d:\Arista\accontantAI\vouching\backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import models
from app.services import reconciliation

def sync():
    db = SessionLocal()
    print("Starting Global Reconciliation Sync (Strict GSTIN Logic)...")
    
    try:
        # Get all extracted invoices
        invoices = db.query(models.ExtractedInvoice).all()
        print(f"Syncing {len(invoices)} invoices...")
        
        for idx, invoice in enumerate(invoices):
            # Re-run reconciliation with new logic
            reconciliation.reconcile_single_invoice(invoice, db)
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(invoices)}...")
                
        print("Sync completed successfully.")
        
    except Exception as e:
        print(f"Sync failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    sync()
