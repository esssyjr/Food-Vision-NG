# 🍲 FOOD VISION V1

A powerful Nigerian food detection and analysis app that **seamlessly integrates Roboflow, Google Gemini AI, Gradio, and Text-to-Speech** technologies. Upload any food image, and the system detects the dish, explains its **health benefits**, **nutritional value**, **suitability for diabetics**, **common ingredients**, and **preparation methods** — with audio output in real time.

> ⚡️ Built to simplify how developers can build intelligent, multimodal systems — from vision to voice — with minimal code!

---

## 🎯 Key Features

- 🧠 **AI-Powered Food Insights** — Get instant health and nutritional data
- 🖼️ **Food Detection** — Uses [Roboflow](https://roboflow.com/) for robust image detection using a pretrained model
- 💬 **Gemini AI Integration** — Summarizes complex food facts into concise and relevant bullet points
- 🔊 **Voice Output** — Uses `gTTS` to speak results aloud
- 🎛️ **Interactive UI** — Powered by [Gradio](https://www.gradio.app/)


---

## ✨ Why This App Matters

This project demonstrates how easy it is to:

- Build **AI-first system** that combine **vision**, **language**, and **voice**
- Create tools for **education**, **health awareness**, and **local cuisine recognition**
- Use cutting-edge APIs to **solve real problems faster** and **reduce development time**

Whether you're a **developer**, **researcher**, or just curious about what's on your plate — this system brings food analysis to life with just an image.

---

## 📸 How It Works

1. **Upload an image** of any food.
2. Click **"Detect Food"**.
3. Choose what you want to learn:
   - ✅ Health Benefits
   - 🍎 Calories & Nutrition
   - 💉 Diabetic Friendliness
   - 🧂 Main Ingredients
   - 🍳 Preparation Method
4. Listen to **AI-generated audio summaries** instantly.

---

## 🔐 Setup Guide

### 1. Clone the Project

```bash
git clone https://github.com/yourusername/food-vision-v1.git
cd food-vision-v1

## 🛠️ Setup Instructions
```
### 2. Install Requirements

```bash
pip install -r requirements.txt
```
### 3. Configure Environment Variables

Create a `.env` file in the root directory and add your API keys:

```env
ROBOFLOW_API_KEY=your_roboflow_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```
> 🧪 **You can get your API keys from:**
> - [Roboflow Dashboard](https://app.roboflow.com/)
> - [Google AI Studio for Gemini](https://makersuite.google.com/)

---

### 4. Run the App

```bash
python app.py

This will launch a local server in your browser using Gradio.
```
---

## 📁 Project Structure

```bash
food-vision-v1/
├── app.py              # Main Gradio app logic
├── .env                # API keys (excluded from version control)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```
## ✍️ Medium Article

I’ve written a detailed breakdown of how I built this app and how you can too using Roboflow, Gemini, and Gradio:

👉 **Read the full article here**: [*[Add your Medium link here](https://medium.com/@ismailismailtj/integrating-gemini-roboflow-gradio-and-hugging-face-to-build-ai-powered-systems-887f4d91f60b)*](#)

---

## 💡 Example Use Cases

- 📚 **Educational Apps** – Teach users about food health
- 📱 **Smart Kitchens** – Detect ingredients and suggest recipes
- 🧪 **AI Research Projects** – Combine computer vision and large language models
- 🏥 **Healthcare Assistants** – Screen meals for diabetic patients

---

## 📜 License

MIT License (or any open-source license of your choice)

---

## 🙌 Acknowledgments

- [Gradio](https://gradio.app)
- [Roboflow](https://roboflow.com)
- [Google Generative AI (Gemini)](https://ai.google.dev/)
- [gTTS – Google Text-to-Speech](https://pypi.org/project/gTTS/)
- Built by **Ismail Ismail Tijjani AND Sunus Muhammad Ibrahim** under **EJAZTECH.AI**

---

> 💬 **Questions? Suggestions?** Open an issue or start a discussion!

---




