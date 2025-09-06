# Handles NER and Classification using Hugging Face Transformers
from transformers import pipeline

# 1. Initialize the NER pipeline for symptom extraction
ner_pipeline = pipeline(
    "ner",
    model="d4data/biomedical-ner-all",
    tokenizer="d4data/biomedical-ner-all",
    aggregation_strategy="simple"
)

# 2. Initialize the Zero-Shot Classification pipeline for categorization
classifier_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def extract_entities(text: str) -> list:
    """Extracts biomedical entities from text."""
    if not text.strip():
        return []
    entities = ner_pipeline(text)
    # Convert numpy types to Python native types for JSON serialization
    for entity in entities:
        if 'score' in entity:
            entity['score'] = float(entity['score'])
    return entities

def classify_problem(text: str) -> dict:
    """Classifies the problem text into predefined categories."""
    if not text.strip():
        return {"label": "unknown", "score": 0.0}
        
    candidate_labels = [
        "dermatology (skin issue)",
        "influenza (flu, cold, fever)",
        "inflammatory (body pain, joint pain, swelling)",
        "gastrointestinal (stomach issue, digestion)",
        "respiratory (breathing issue, cough)",
        "general inquiry"
    ]
    
    result = classifier_pipeline(text, candidate_labels)
    # The top result is the first in the list
    # Convert numpy types to Python native types for JSON serialization
    return {"label": result['labels'][0], "score": float(result['scores'][0])}
