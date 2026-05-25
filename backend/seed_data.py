from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import models
from datetime import datetime, timedelta

def seed_db():
    db = SessionLocal()
    
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    # 1. Create User
    user = models.User(email="article@arista.ai", hashed_password="hashed_password", role=models.UserRole.ARTICLE)
    db.add(user)
    
    # 2. Create Clients
    clients = [
        models.Client(name="Acme Corp", pan="ABCDE1234F", gstin="27ABCDE1234F1Z5", address="Mumbai, MH"),
        models.Client(name="Globex Inc", pan="FGHIJ5678K", gstin="24FGHIJ5678K1Z2", address="Ahmedabad, GJ"),
    ]
    for c in clients:
        db.add(c)
    db.commit()
    
    # 3. Create Engagement
    eng = models.Engagement(
        client_id=clients[0].id,
        period_start=datetime(2026, 3, 1),
        period_end=datetime(2026, 3, 31),
        status="active"
    )
    db.add(eng)
    db.commit()
    
    # 4. Create Register
    reg = models.Register(
        engagement_id=eng.id,
        register_type="purchase",
        filename="Purchase_Register_March.xlsx",
        file_path="storage/registers/Purchase_Register_March.xlsx"
    )
    db.add(reg)
    db.commit()
    
    # 5. Create Register Rows
    reg_rows = [
        models.RegisterRow(
            register_id=reg.id,
            invoice_number="INV/2024/001",
            invoice_date=datetime(2026, 3, 25),
            vendor_name="Reliance Retail",
            vendor_gstin="27AAACR1234F1Z1",
            taxable_value=10550.0,
            total_value=12450.0
        ),
        models.RegisterRow(
            register_id=reg.id,
            invoice_number="TEL/MARCH/99",
            invoice_date=datetime(2026, 3, 24),
            vendor_name="Airtel Business",
            vendor_gstin="27AABCA5678R1Z2",
            taxable_value=1780.0,
            total_value=2100.0
        )
    ]
    for row in reg_rows:
        db.add(row)
    db.commit()
    
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_db()
