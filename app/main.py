from fastapi import FastAPI, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from .database import engine, Base, SessionLocal
from . import models, schemas, crud

app = FastAPI(
    title="Finance Tracking System",
    description="Python backend for managing income, expenses, and financial summaries",
    version="1.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple role simulation using header (X-Role: admin / analyst / viewer)
def get_current_role(x_role: Optional[str] = Header(None)):
    allowed_roles = ["viewer", "analyst", "admin"]
    if not x_role or x_role not in allowed_roles:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing X-Role header. Use: viewer, analyst, or admin"
        )
    return x_role

# Seed some sample data when server starts
@app.on_event("startup")
def seed_sample_data():
    db = SessionLocal()
    if db.query(models.Transaction).count() == 0:
        samples = [
            schemas.TransactionCreate(amount=45000, transaction_type="income", category="Salary", date=date(2026, 3, 1), description="March Salary"),
            schemas.TransactionCreate(amount=1200, transaction_type="expense", category="Rent", date=date(2026, 3, 5), description="Monthly Rent"),
            schemas.TransactionCreate(amount=8500, transaction_type="income", category="Freelance", date=date(2026, 3, 10), description="Web development project"),
            schemas.TransactionCreate(amount=450, transaction_type="expense", category="Food", date=date(2026, 3, 15), description="Groceries"),
            schemas.TransactionCreate(amount=300, transaction_type="expense", category="Transport", date=date(2026, 3, 20), description="Fuel"),
        ]
        for sample in samples:
            crud.create_transaction(db, sample)
        print("✅ Sample data added successfully!")
    db.close()

# ==================== API Endpoints ====================

@app.post("/transactions/", response_model=schemas.TransactionRead)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db), 
    role: str = Depends(get_current_role)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can create transactions")
    return crud.create_transaction(db, transaction)

@app.get("/transactions/")
def read_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    role: str = Depends(get_current_role)
):
    return crud.get_transactions(db, skip, limit, transaction_type, category, date_from, date_to)

@app.get("/transactions/{transaction_id}", response_model=schemas.TransactionRead)
def read_single_transaction(transaction_id: int, db: Session = Depends(get_db), role: str = Depends(get_current_role)):
    transaction = crud.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.put("/transactions/{transaction_id}", response_model=schemas.TransactionRead)
def update_transaction(
    transaction_id: int, 
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db), 
    role: str = Depends(get_current_role)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can update")
    updated = crud.update_transaction(db, transaction_id, transaction)
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), role: str = Depends(get_current_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can delete")
    deleted = crud.delete_transaction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

@app.get("/summaries/")
def get_financial_summary(db: Session = Depends(get_db), role: str = Depends(get_current_role)):
    summary = crud.get_summary(db)
    if role == "viewer":
        # Viewer gets only basic summary
        summary.pop("category_breakdown", None)
        summary.pop("recent_activity", None)
    return summary

@app.get("/")
def home():
    return {"message": "Finance Tracking Backend is running! Visit /docs for API documentation"}