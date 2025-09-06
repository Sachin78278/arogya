# SQLAlchemy table models
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base
import json

class PatientQuery(Base):
    __tablename__ = "patient_queries"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_text = Column(Text, nullable=False)
    extracted_symptoms = Column(Text, nullable=True)  # Storing as a JSON string
    problem_category = Column(String, nullable=True)
    category_confidence = Column(String, nullable=True)
