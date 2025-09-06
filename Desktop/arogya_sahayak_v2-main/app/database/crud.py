# Functions to create/read database entries
from sqlalchemy.orm import Session
from . import models
import json
import numpy as np

# ADD THIS HELPER FUNCTION
def numpy_converter(obj):
    """Converts numpy types to their native Python equivalents for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def create_patient_query(db: Session, raw_text: str, symptoms: list, category: str, confidence: float):
    # Storing as a JSON string, using our custom converter
    symptoms_json = json.dumps(symptoms, default=numpy_converter)

    db_query = models.PatientQuery(
        raw_text=raw_text,
        extracted_symptoms=symptoms_json,
        problem_category=category,
        category_confidence=str(confidence)
    )

    db.add(db_query)
    db.commit()
    db.refresh(db_query)

    return db_query