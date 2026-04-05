from sqlalchemy import Column, Integer, String, Float, Date, Text
from .database import Base
from datetime import date

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # "income" or "expense"
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)