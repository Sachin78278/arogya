# Pydantic models for API validation
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class IntakeResponse(BaseModel):
    """The final response model returned by the /intake endpoint."""
    message: str
    database_record_id: int
    timestamp: datetime
    problem_category: str
    category_confidence: float
    extracted_symptoms: List[Dict[str, Any]]
    full_text: str
