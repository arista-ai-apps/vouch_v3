from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, SessionLocal
from .models import models
from .api import clients, engagements, files, reconciliation, exceptions, registers, bill_of_sale, hsn

from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

def seed_default_data():
    db = SessionLocal()
    try:
        if db.query(models.Client).count() == 0:
            client = models.Client(id=1, name="RB Systems", pan="AAACR1234P", gstin="27RBSYS1234P1Z1", address="Mumbai")
            db.add(client)
            db.flush()
            engagement = models.Engagement(id=12, client_id=1, period_start=datetime(2026, 4, 1), period_end=datetime(2026, 4, 30), status="active")
            db.add(engagement)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

seed_default_data()

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

app.include_router(clients.router, prefix=settings.API_V1_STR)
app.include_router(engagements.router, prefix=settings.API_V1_STR)
app.include_router(files.router, prefix=settings.API_V1_STR)
app.include_router(registers.router, prefix=settings.API_V1_STR)
app.include_router(reconciliation.router, prefix=settings.API_V1_STR)
app.include_router(exceptions.router, prefix=settings.API_V1_STR)
app.include_router(bill_of_sale.router, prefix=settings.API_V1_STR)
app.include_router(hsn.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Arista AI SV-CIE API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
