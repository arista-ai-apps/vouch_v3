import sys
import os

# Add the parent directory to sys.path to import from 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.tax_validator import validate_tax_type
from app.models import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup an in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)
db = Session()
models.Base.metadata.create_all(bind=engine)

def test_tax_validation():
    # Setup mock engagement and file
    engagement = models.Engagement(id=1, client_id=1)
    db.add(engagement)
    file = models.UploadedFile(id=1, engagement_id=1, filename="test.pdf")
    db.add(file)
    db.commit()

    # Test Case 1: Intra-state (Same State Code) - Correct Tax
    # MH (27) to MH (27)
    inv1 = models.ExtractedInvoice(
        id=1, file_id=1, vendor_gstin="27AAAAA0000A1Z5", buyer_gstin="27BBBBB0000B1Z5",
        cgst=100.0, sgst=100.0, igst=0.0
    )
    res1 = validate_tax_type(inv1, db)
    print(f"Test 1 (Intra Correct): Status={res1.status}, Mismatch={res1.is_mismatch}")
    assert res1.status == "CLEARED"

    # Test Case 2: Intra-state (Same State Code) - Wrong Tax (IGST instead of CGST+SGST)
    inv2 = models.ExtractedInvoice(
        id=2, file_id=1, vendor_gstin="27AAAAA0000A1Z5", buyer_gstin="27BBBBB0000B1Z5",
        cgst=0.0, sgst=0.0, igst=200.0
    )
    res2 = validate_tax_type(inv2, db)
    print(f"Test 2 (Intra Wrong): Status={res2.status}, Mismatch={res2.is_mismatch}")
    assert res2.status == "MISMATCH"
    assert "Replace IGST with CGST + SGST/UTGST" in res2.suggestion

    # Test Case 3: Inter-state (Different State Code) - Correct Tax
    # MH (27) to KA (29)
    inv3 = models.ExtractedInvoice(
        id=3, file_id=1, vendor_gstin="27AAAAA0000A1Z5", buyer_gstin="29BBBBB0000B1Z5",
        cgst=0.0, sgst=0.0, igst=200.0
    )
    res3 = validate_tax_type(inv3, db)
    print(f"Test 3 (Inter Correct): Status={res3.status}, Mismatch={res3.is_mismatch}")
    assert res3.status == "CLEARED"

    # Test Case 4: Inter-state (Different State Code) - Wrong Tax (CGST+SGST instead of IGST)
    inv4 = models.ExtractedInvoice(
        id=4, file_id=1, vendor_gstin="27AAAAA0000A1Z5", buyer_gstin="29BBBBB0000B1Z5",
        cgst=100.0, sgst=100.0, igst=0.0
    )
    res4 = validate_tax_type(inv4, db)
    print(f"Test 4 (Inter Wrong): Status={res4.status}, Mismatch={res4.is_mismatch}")
    assert res4.status == "MISMATCH"
    assert "Replace CGST + SGST/UTGST with IGST" in res4.suggestion

    # Test Case 5: Missing GSTIN - Needs Review
    inv5 = models.ExtractedInvoice(
        id=5, file_id=1, vendor_gstin=None, buyer_gstin=None,
        cgst=100.0, sgst=100.0, igst=0.0
    )
    res5 = validate_tax_type(inv5, db)
    print(f"Test 5 (Missing Info): Status={res5.status}, Mismatch={res5.is_mismatch}")
    assert res5.status == "NEEDS_REVIEW"

    print("\nAll tests passed!")

if __name__ == "__main__":
    test_tax_validation()
