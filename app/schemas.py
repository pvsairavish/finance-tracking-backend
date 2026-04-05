from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Literal

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    transaction_type: Literal["income", "expense"]
    category: str
    date: date
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int

    class Config:
        from_attributes = True