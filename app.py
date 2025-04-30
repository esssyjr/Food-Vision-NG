import gradio as gr
from PIL import Image
import tempfile
import os
from inference_sdk import InferenceHTTPClient
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "nigeria-food/2"

# Initialize APIs
roboflow_client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Function to get food information with specific focus
def get_food_info(food_names, info_type):
    food_query = ", ".join(food_names)
    
    prompts = {
        "benefits": f"""
        Provide a BRIEF summary of the health benefits of {food_query}.
        If this is not Nigerian cuisine, still provide useful benefits information.
        Focus only on PROVEN health benefits.
        Keep your answer under 100 words and use bullet points.
        """,
        
        "calories": f"""
        Provide a BRIEF overview of the caloric content and macronutrients in {food_query}.
        If this is not Nigerian cuisine, still provide approximate nutritional information.
        Include calories per serving, protein, carbs, and fats if known.
        Keep your answer under 100 words and use bullet points.
        """,
        
        "diabetic": f"""
        Explain BRIEFLY if {food_query} is suitable for diabetic patients.
        Consider glycemic index, carb content, and potential blood sugar impact.
        If this is not Nigerian cuisine, still provide relevant information for diabetics.
        Keep your answer under 100 words and use bullet points.
        """,
        
        "ingredients": f"""
        List the main ingredients typically found in {food_query}.
        If this is not Nigerian cuisine, still list common ingredients.
        Keep your answer under 100 words and use bullet points.
        """,
        
        "preparation": f"""
        Give a BRIEF overview of how {food_query} is typically prepared.
        If this is not Nigerian cuisine, still provide basic preparation method.
        Keep your answer under 100 words and use bullet points.
        """
    }
    
    try:
        # Get response from Gemini AI
        response = model.generate_content(prompts[info_type])
        return response.text
    except Exception as e:
        return f"Error getting information: {str(e)}"

# Function to convert text to speech
def text_to_speech(text, language='en'):
    tts = gTTS(text=text, lang=language)
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(audio_file.name)
    return audio_file.name

# Function to process the uploaded image
def detect_food(image):
    if image is None:
        return "Please upload an image first.", [], gr.update(visible=False)
    
    try:
        # Save the uploaded image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image_pil = Image.fromarray(image)  # Convert the numpy array to a PIL Image
            image_pil.save(tmp_file, format='JPEG')
            temp_file_path = tmp_file.name
        
        # Send to Roboflow for detection using the file path
        result = roboflow_client.infer(temp_file_path, model_id=MODEL_ID)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Process the result
        if "predictions" in result and len(result["predictions"]) > 0:
            predictions = result["predictions"]
            
            # Sort predictions by confidence
            predictions.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            
            # Get top predictions (confidence > 20%)
            top_predictions = [pred for pred in predictions if pred.get("confidence", 0) > 0.2]
            
            # Get food names for all top predictions
            food_names = [pred.get("class", "Unknown") for pred in top_predictions]
            
            # Create detection result text
            if len(food_names) == 1:
                detection_result = f"This is {food_names[0]}! What would you like to know about it?"
            else:
                food_list = ", ".join(food_names[:-1]) + " and " + food_names[-1] if len(food_names) > 1 else food_names[0]
                detection_result = f"This is {food_list}! What would you like to know about these foods?"
            
            return detection_result, food_names, gr.update(visible=True)
        else:
            return "No food detected in the image. Please try a different image.", [], gr.update(visible=False)
    
    except Exception as e:
        # Clean up in case of error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        return f"Error in detection: {str(e)}", [], gr.update(visible=False)

# Create dedicated handler functions for each button
def show_benefits(detected_foods):
    info = get_food_info(detected_foods, "benefits")
    audio_file = text_to_speech(info, language='en')  # Convert Gemini output to speech
    return info, audio_file

def show_calories(detected_foods):
    info = get_food_info(detected_foods, "calories")
    audio_file = text_to_speech(info, language='en')
    return info, audio_file

def show_diabetic(detected_foods):
    info = get_food_info(detected_foods, "diabetic")
    audio_file = text_to_speech(info, language='en')
    return info, audio_file

def show_ingredients(detected_foods):
    info = get_food_info(detected_foods, "ingredients")
    audio_file = text_to_speech(info, language='en')
    return info, audio_file

def show_preparation(detected_foods):
    info = get_food_info(detected_foods, "preparation")
    audio_file = text_to_speech(info, language='en')
    return info, audio_file

# Create Gradio interface with theme
theme = gr.themes.Soft(
    primary_hue="orange",
    secondary_hue="blue",
)

with gr.Blocks(title="Nigerian Food Detector with Voice Output", theme=theme) as demo:
    gr.Markdown("# FOOD VISION V1")
    
    # Store detected foods for button actions
    detected_foods_state = gr.State([])

    # Create layout
    with gr.Row():
        input_image = gr.Image(label="Upload Food Image", type="numpy")
    
    detect_button = gr.Button("Detect Food", variant="primary", size="lg")
    
    # Result and options section
    detection_text = gr.Markdown()
    
    # Option buttons (initially hidden)
    options_row = gr.Row(visible=False)
    with options_row:
        benefits_btn = gr.Button("Health Benefits", size="sm")
        calories_btn = gr.Button("Calories & Nutrition", size="sm")
        diabetic_btn = gr.Button("Diabetic Friendly?", size="sm")
        ingredients_btn = gr.Button("Main Ingredients", size="sm")
        preparation_btn = gr.Button("Preparation Method", size="sm")
    
    # Information display
    info_display = gr.Markdown()
    audio_output = gr.Audio()

    # Set up detection event
    detect_button.click(
        fn=detect_food,
        inputs=[input_image],
        outputs=[detection_text, detected_foods_state, options_row]
    )
    
    # Set up button click events
    benefits_btn.click(
        fn=show_benefits,
        inputs=[detected_foods_state],
        outputs=[info_display, audio_output]
    )
    
    calories_btn.click(
        fn=show_calories,
        inputs=[detected_foods_state],
        outputs=[info_display, audio_output]
    )
    
    diabetic_btn.click(
        fn=show_diabetic,
        inputs=[detected_foods_state],
        outputs=[info_display, audio_output]
    )
    
    ingredients_btn.click(
        fn=show_ingredients,
        inputs=[detected_foods_state],
        outputs=[info_display, audio_output]
    )
    
    preparation_btn.click(
        fn=show_preparation,
        inputs=[detected_foods_state],
        outputs=[info_display, audio_output]
    )
    
    gr.Markdown("---")
    gr.Markdown("Powered by EJAZTECH.AI")

# Launch the app
if __name__ == "__main__":
    demo.launch()
