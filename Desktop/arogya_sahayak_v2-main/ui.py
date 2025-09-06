


# In ui.py

import gradio as gr
import requests
import json

# The URL of our running FastAPI backend
API_URL = "http://127.0.0.1:8000/intake"

def process_inputs(text_input, audio_file, image_file):
    """
    This function takes inputs from the Gradio interface, sends them to the FastAPI
    backend, and returns the formatted response.
    """
    # Create the payload to send to the API.
    # The 'requests' library can handle a mix of files and data.
    files = {}
    if audio_file is not None:
        files["audio_file"] = open(audio_file, "rb")
    if image_file is not None:
        # Gradio provides the image as a numpy array, we need to save it first
        # This is a simplified way; for production, use a temporary file.
        image_file.save("temp_image.png")
        files["image_file"] = open("temp_image.png", "rb")

    data = {}
    if text_input:
        data["text_input"] = text_input

    try:
        # Make the POST request to the FastAPI backend
        response = requests.post(API_URL, files=files, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # Format the JSON response for clean display
        result = response.json()
        
        # Create a user-friendly markdown output with enhanced styling
        output_markdown = f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 10px; color: white; margin: 20px 0;">
            <h2 style="margin: 0; font-size: 24px;">✅ Query Processed Successfully!</h2>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #007bff;">
            <h3 style="margin: 0 0 10px 0; color: #007bff;">📋 Database Record</h3>
            <p style="margin: 0; font-family: monospace; background: #e9ecef; padding: 8px; border-radius: 4px;">
                <strong>Record ID:</strong> {result['database_record_id']}
            </p>
        </div>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107;">
            <h3 style="margin: 0 0 10px 0; color: #856404;">🎯 AI Classification</h3>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="background: #007bff; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold;">
                    {result['problem_category']}
                </span>
                <span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold;">
                    {result['category_confidence']:.1%} confidence
                </span>
            </div>
        </div>

        <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #17a2b8;">
            <h3 style="margin: 0 0 15px 0; color: #0c5460;">🔍 Extracted Symptoms & Entities</h3>
        """
        
        if result['extracted_symptoms']:
            output_markdown += "<div style='display: flex; flex-wrap: wrap; gap: 8px;'>"
            for entity in result['extracted_symptoms']:
                output_markdown += f"""
                <span style="background: #17a2b8; color: white; padding: 6px 12px; border-radius: 20px; font-size: 14px; margin: 2px;">
                    <strong>{entity['word']}</strong> <small>({entity['entity_group']})</small>
                </span>
                """
            output_markdown += "</div>"
        else:
            output_markdown += """
            <div style="text-align: center; color: #6c757d; font-style: italic; padding: 20px;">
                <p style="margin: 0;">🔍 No specific medical entities were extracted from the input.</p>
                <p style="margin: 5px 0 0 0; font-size: 14px;">This could mean the input was general or the AI needs more specific medical terms.</p>
            </div>
            """
        
        output_markdown += "</div>"
        
        # Add full text section
        output_markdown += f"""
        <div style="background: #e2e3e5; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #6c757d;">
            <h3 style="margin: 0 0 10px 0; color: #495057;">📄 Full Processed Text</h3>
            <p style="margin: 0; background: white; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 14px; line-height: 1.4;">
                {result['full_text']}
            </p>
        </div>
        """

        return output_markdown

    except requests.exceptions.RequestException as e:
        return f"## ❌ Error\n\nCould not connect to the API backend. Please ensure the server is running.\n\n**Details:** {e}"
    except Exception as e:
        return f"## ❌ An Unexpected Error Occurred\n\n**Details:** {e}"


# Define the Gradio interface with enhanced styling
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Textbox(
            lines=5, 
            label="📝 Describe your symptoms in text (Supports English, Hindi, and Punjabi)",
            placeholder="Enter your symptoms here... (e.g., 'I have a fever and headache')"
        ),
        gr.Audio(
            type="filepath", 
            label="🎤 Record or upload your symptoms (Click to record or upload an audio file)"
        ),
        gr.Image(
            type="pil", 
            label="📄 Upload a prescription or medical image (Upload documents, prescriptions, or medical images)"
        )
    ],
    outputs=gr.Markdown(label="📊 AI Analysis Results"),
    title="🩺 Arogya Sahayak v2 - Intelligent Patient Intake",
    description="""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin: 20px 0;">
        <h2 style="margin: 0; font-size: 24px;">🏥 Welcome to Arogya Sahayak v2</h2>
        <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
            Your intelligent health assistant powered by AI. Describe your symptoms through text, voice, or images, 
            and get instant medical category classification and symptom extraction.
        </p>
    </div>
    <div style="text-align: center; margin: 20px 0;">
        <p style="font-size: 14px; color: #666;">
            💡 <strong>Tip:</strong> You can use any combination of inputs - text, audio, or images. 
            The AI will process all provided information together.
        </p>
    </div>
    """,
    allow_flagging="never",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="slate"
    ),
    css="""
    .gradio-container {
        max-width: 1000px !important;
        margin: 0 auto !important;
    }
    .main-header {
        text-align: center !important;
        margin-bottom: 30px !important;
    }
    .input-section {
        background: #f8f9fa !important;
        padding: 20px !important;
        border-radius: 10px !important;
        margin: 10px 0 !important;
        border: 1px solid #e9ecef !important;
    }
    .output-section {
        background: #fff !important;
        padding: 20px !important;
        border-radius: 10px !important;
        margin: 10px 0 !important;
        border: 2px solid #007bff !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    """
)

# Launch the UI
if __name__ == "__main__":
    iface.launch()
