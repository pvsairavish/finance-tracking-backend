from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date
from collections import defaultdict
from typing import Optional

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        date=transaction.date,
        description=transaction.description,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    query = db.query(models.Transaction)
    if transaction_type:
        query = query.filter(models.Transaction.transaction_type == transaction_type)
    if category:
        query = query.filter(models.Transaction.category == category)
    if date_from:
        query = query.filter(models.Transaction.date >= date_from)
    if date_to:
        query = query.filter(models.Transaction.date <= date_to)
    return query.offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionCreate):
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db_transaction.amount = transaction.amount
        db_transaction.transaction_type = transaction.transaction_type
        db_transaction.category = transaction.category
        db_transaction.date = transaction.date
        db_transaction.description = transaction.description
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction

def get_summary(db: Session):
    transactions = db.query(models.Transaction).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense")
    balance = total_income - total_expenses

    # Category wise breakdown
    category_breakdown = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for t in transactions:
        category_breakdown[t.category][t.transaction_type] += t.amount

    # Recent 5 transactions
    recent_activity = sorted(transactions, key=lambda t: t.date, reverse=True)[:5]
    recent = [
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.transaction_type,
            "category": t.category,
            "date": t.date.isoformat(),
            "description": t.description,
        }
        for t in recent_activity
    ]

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "current_balance": round(balance, 2),
        "category_breakdown": dict(category_breakdown),
        "recent_activity": recent,
        "total_transactions": len(transactions),
    }