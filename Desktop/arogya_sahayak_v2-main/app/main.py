# main.py
# FastAPI app declaration and API endpoints

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
import os
import tempfile
import logging

from app.schemas import IntakeResponse
from app.services import stt_service, ocr_service, nlu_service
from app.database import crud, models
from app.database.database import SessionLocal, engine

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create the database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Arogya Sahayak v2 API")


# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Welcome to Arogya Sahayak v2"}


@app.post("/intake", response_model=IntakeResponse)
async def process_intake(
    db: Session = Depends(get_db),
    text_input: Annotated[str | None, Form()] = None,
    audio_file: UploadFile | None = File(None),
    image_file: UploadFile | None = File(None)
):
    if not text_input and not audio_file and not image_file:
        raise HTTPException(status_code=400, detail="No input provided.")

    # 1. Process all inputs into text
    full_text_parts = []

    # Text input
    if text_input:
        full_text_parts.append(text_input)

    # Audio input
    if audio_file:
        logging.info(f"✅ Received audio file: {audio_file.filename}, type={audio_file.content_type}")

        # Always force .wav suffix
        suffix = ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await audio_file.read())
            tmp_path = tmp.name

        try:
            text_from_audio = stt_service.transcribe_audio(tmp_path)
            full_text_parts.append(text_from_audio)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # Image input
    if image_file:
        extracted_text = ocr_service.extract_text_from_image(image_file)
        full_text_parts.append(extracted_text)

    # Combine all extracted text
    combined_text = " ".join(part for part in full_text_parts if part)

    if not combined_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from inputs.")

    # 2. Run NLU analysis
    symptoms = nlu_service.extract_entities(combined_text)
    classification_result = nlu_service.classify_problem(combined_text)
    
    # Debug logging
    logging.info(f"Classification result: {classification_result}")
    
    # Extract category and confidence with error handling
    category = classification_result.get("label", "unknown")
    confidence_raw = classification_result.get("score", 0.0)
    
    # Ensure confidence is a valid float
    try:
        confidence = float(confidence_raw)
    except (ValueError, TypeError) as e:
        logging.error(f"Error converting confidence to float: {e}, raw value: {confidence_raw}")
        confidence = 0.0

    # 3. Store the structured result in the database
    db_record = crud.create_patient_query(db, combined_text, symptoms, category, confidence)

    # 4. Return the structured response
    return IntakeResponse(
        message="Patient query processed and stored successfully.",
        database_record_id=int(db_record.id),
        timestamp=db_record.created_at,
        problem_category=str(db_record.problem_category),
        category_confidence=float(db_record.category_confidence),
        extracted_symptoms=symptoms,
        full_text=combined_text
    )
