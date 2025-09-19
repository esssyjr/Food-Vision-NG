from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
import tempfile
from google import generativeai
import random
import io
import logging
from pydantic import BaseModel
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from fastapi.responses import FileResponse
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App initialization
app = FastAPI(title="Nigerian Food Vision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set API Keys
API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1", "AIzaSyBvtwP2ulNHPQexfPhhR13U30pvF2OswrU"),
    os.getenv("GOOGLE_API_KEY_2", "AIzaSyD0dLXPPrZmLbnHOj3f9twHmT_PZc15wMo"),
    os.getenv("GOOGLE_API_KEY_3", "AIzaSyCKYS00SLw0-vOLaPbhCPjK2ghpA5jrj9A"),
    os.getenv("GOOGLE_API_KEY_4", "AIzaSyAvcvFgl-gjutXpsLW_jnC-zSs6lTXXiU0"),
]

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_KEY")

# Model options
INFO_OPTIONS = [
    "Calories content",
    "Diabetic friendly?",
    "Preparation method",
    "Ingredients",
    "Nutritional content",
    "Allergen info",
    "Hypertension friendly?",
    "Kidney safe?"
]

# Configure Gemini
def configure_gemini():
    api_key = random.choice(API_KEYS)
    if not api_key:
        raise ValueError("No valid API key provided.")
    generativeai.configure(api_key=api_key)
    return generativeai.GenerativeModel("gemini-1.5-flash")

# ================= DETECT FOOD =================
@app.post("/detect_food")
async def detect_food(image: UploadFile = File(...), lang: str = Form(default="english")):
    try:
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))

        if img.format not in ["JPEG", "PNG"]:
            raise HTTPException(status_code=400, detail="Only JPEG or PNG images are supported.")

        # 🔥 Fix: Convert RGBA to RGB (to handle transparency before saving as JPEG)
        if img.mode == "RGBA":
            img = img.convert("RGB")

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            img.save(temp_file.name, format="JPEG")
            image_path = temp_file.name

        model = configure_gemini()
        uploaded = generativeai.upload_file(path=image_path, mime_type="image/jpeg")

        prompt = f"Identify the name of the food shown in the image. Respond with ONLY the name (e.g., Jollof rice, Egusi soup, etc)."
        response = model.generate_content([uploaded, prompt])
        os.unlink(image_path)

        food_name = response.text.strip()

        return {
            "food_name": food_name,
            "options": INFO_OPTIONS
        }

    except Exception as e:
        logger.error(f"Error in detect_food: {e}")
        raise HTTPException(status_code=500, detail=f"Detection error: {e}")


# ================= FOOD INFO =================
class InfoRequest(BaseModel):
    food_name: str
    info_type: str  # e.g., "Calories content"
    diseases: list[str] = []

@app.post("/food_info")
async def food_info(request: InfoRequest):
    try:
        model = configure_gemini()

        disease_info = f" The person has these underlying conditions: {', '.join(request.diseases)}." if request.diseases else ""
        prompt = (
            f"You are a food detection expert. Give specific information about {request.food_name}. "
            f"The user is asking: '{request.info_type}'.{disease_info} "
            f"Provide the answer in a friendly, short, and informative tone."
        )
        response = model.generate_content(prompt)

        return {
            "food_name": request.food_name,
            "info_type": request.info_type,
            "diseases": request.diseases,
            "response": response.text.strip()
        }

    except Exception as e:
        logger.error(f"Error in food_info: {e}")
        raise HTTPException(status_code=500, detail=f"Info error: {e}")

# ================= PREPARATION VIDEO =================
class PrepareRequest(BaseModel):
    food_name: str
    diseases: list[str] = []

@app.post("/prepare_food")
async def prepare_food(request: PrepareRequest):
    try:
        query = f"How to prepare {request.food_name}"
        url = (
            f"https://www.googleapis.com/youtube/v3/search?part=snippet"
            f"&q={query}&key={YOUTUBE_API_KEY}&maxResults=1&type=video"
        )
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        if not data.get("items"):
            return {
                "food_name": request.food_name,
                "preparation_video": "No preparation video found on YouTube.",
                "diseases": request.diseases
            }

        item = data["items"][0]
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        link = f"https://www.youtube.com/watch?v={video_id}"

        return {
            "food_name": request.food_name,
            "preparation_video": {"title": title, "link": link},
            "diseases": request.diseases
        }

    except Exception as e:
        logger.error(f"Error in prepare_food: {e}")
        raise HTTPException(status_code=500, detail=f"Preparation video error: {e}")

# ================= PDF EXPORT =================
class PDFRequest(BaseModel):
    food_name: str
    info: dict  # { "Calories content": "xx", "Ingredients": "yy", ... }
    diseases: list[str] = []
    preparation_video: dict = None  # { "title": "xx", "link": "yy" }

@app.post("/generate_pdf")
async def generate_pdf(request: PDFRequest):
    try:
        file_name = f"{request.food_name.replace(' ', '_')}_report.pdf"
        file_path = os.path.join(tempfile.gettempdir(), file_name)

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(f"Food Report: {request.food_name}", styles["Title"]))
        story.append(Spacer(1, 12))

        # Underlying Diseases
        if request.diseases:
            story.append(Paragraph(f"Underlying conditions: {', '.join(request.diseases)}", styles["Normal"]))
            story.append(Spacer(1, 12))

        # Food Info Section
        story.append(Paragraph("Food Information:", styles["Heading2"]))
        for key, value in request.info.items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", styles["Normal"]))
            story.append(Spacer(1, 8))

        # Preparation Video Section
        if request.preparation_video:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Preparation Video:", styles["Heading2"]))
            story.append(Paragraph(f"{request.preparation_video['title']}", styles["Normal"]))
            story.append(Paragraph(f"Link: {request.preparation_video['link']}", styles["Normal"]))

        doc.build(story)

        return FileResponse(file_path, media_type="application/pdf", filename=file_name)

    except Exception as e:
        logger.error(f"Error in generate_pdf: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation error: {e}")

# ================= ROOT =================
@app.get("/")
async def root():
    return {
        "message": "Welcome to Nigerian Food Vision API. Endpoints available: /detect_food, /food_info, /prepare_food, /generate_pdf"
    }
