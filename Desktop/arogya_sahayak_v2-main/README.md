# Arogya Sahayak v2 - Intelligent Patient Intake

This application serves as a proof-of-concept for an intelligent system to capture and structure patient health queries.

## Core Features
- **Multimodal Input**: Accepts text, voice (Hindi/English/Punjabi), and images.
- **Symptom Extraction**: Uses a biomedical NER model to identify key symptoms.
- **Problem Classification**: Uses a Zero-Shot model to categorize the issue into types like dermatology, influenza, etc.
- **Structured Storage**: Saves the processed information neatly in a SQLite database.

## Setup
1.  Clone the repository.
2.  Install Google's Tesseract OCR engine on your system.
3.  Install Python dependencies: `pip install -r requirements.txt`
4.  (On first run, the necessary AI models from Hugging Face and OpenAI will be downloaded. This may take some time and storage space.)

## How to Run
1.  Start the FastAPI server from the root directory:
    ```bash
    uvicorn app.main:app --reload
    ```
2.  Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs` to test the `/intake` endpoint.
