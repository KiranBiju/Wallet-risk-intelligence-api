from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RiskReport(Base):
    __tablename__ = "risk_reports"

    wallet = Column(String, primary_key=True)
    risk_level = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)