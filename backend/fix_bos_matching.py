from app.core.database import SessionLocal
from app.models import models
from app.services import reconciliation

def fix():
    db = SessionLocal()
    print("Fetching all extracted Bills of Sale...")
    bos_list = db.query(models.ExtractedBillOfSale).all()
    print(f"Found {len(bos_list)} entries. Starting reconciliation...")
    
    for bos in bos_list:
        print(f"Matching BOS {bos.sale_number}...")
        reconciliation.reconcile_single_bill_of_sale(bos, db)
    
    print("Done!")
    db.close()

if __name__ == "__main__":
    fix()
