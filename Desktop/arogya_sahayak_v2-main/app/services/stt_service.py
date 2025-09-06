import whisper
import os
from fastapi import UploadFile

# Load the "large" Whisper model for maximum accuracy
model = whisper.load_model("large")  # "large" provides the highest accuracy

def transcribe_audio(audio_file_path: str, preferred_language: str = None) -> str:
    try:
        print(f"Starting transcription for: {audio_file_path}")
        
        # Use preferred language if specified, otherwise auto-detect
        if preferred_language:
            print(f"Using preferred language: {preferred_language}")
            result = model.transcribe(
                audio_file_path, 
                language=preferred_language,
                fp16=False,
                verbose=False
            )
        else:
            # Auto-detect language and transcribe
            result = model.transcribe(
                audio_file_path, 
                fp16=False,
                verbose=False
            )
            
            # Get detected language from result
            detected_language = result.get("language", "unknown")
            print(f"Auto-detected language: {detected_language}")
            
            # Map similar languages to preferred ones for better Indian language support
            language_mapping = {
                'ur': 'hi',  # Map Urdu to Hindi for better Indian language support
                'pa': 'hi',  # Map Punjabi to Hindi
                'hi': 'hi',  # Keep Hindi as is
                'en': 'en'   # Keep English as is
            }
            
            # For Indian languages, try Hindi first if detection is uncertain
            if detected_language in ['ur', 'pa', 'hi'] or detected_language == 'unknown':
                print(f"Attempting Hindi transcription for better Indian language support")
                try:
                    hindi_result = model.transcribe(
                        audio_file_path, 
                        language='hi',
                        fp16=False,
                        verbose=False
                    )
                    hindi_text = hindi_result.get("text", "").strip()
                    if hindi_text and len(hindi_text) > 2:  # If we get meaningful Hindi text
                        print(f"Hindi transcription successful: '{hindi_text}'")
                        return hindi_text
                except Exception as e:
                    print(f"Hindi transcription failed: {e}")
                    pass
            
            # If detected language should be mapped, re-transcribe with mapped language
            if detected_language in language_mapping and language_mapping[detected_language] != detected_language:
                target_language = language_mapping[detected_language]
                print(f"Re-transcribing with mapped language: {detected_language} -> {target_language}")
                result = model.transcribe(
                    audio_file_path, 
                    language=target_language,
                    fp16=False,
                    verbose=False
                )
        
        transcribed_text = result.get("text", "").strip()
        print(f"Transcribed text: '{transcribed_text}'")
        
        return transcribed_text
        
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        import traceback
        traceback.print_exc()
        return ""
