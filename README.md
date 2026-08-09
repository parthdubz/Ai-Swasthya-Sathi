# AI Swasthya Sathi
---
## 📌 About the Project
**AI Swasthya Sathi** is a smart healthcare assistant that leverages **AI** to provide **intelligent symptom analysis, patient monitoring, and personalized recommendations**.  
It is designed to bridge the gap between patients and medical guidance using cutting-edge **computer vision**, **natural language processing**, and **real-time analytics**.

---

## 💡 Problem Statement
Many patients face delays in initial diagnosis and struggle to track symptoms consistently. Hospitals often lack automated tools for initial screening and monitoring. Especially elderly or those living alone, often cannot communicate health issues immediately, and doctors have no real-time way to monitor symptoms or respond quickly in emergencies.
**AI Swasthya Sathi** addresses this by providing:

- Quick symptom detection  
- Real-time monitoring using AI  
- Easy-to-use interface for patients and healthcare staff  

---

## ⚙️ Features
- AI-powered **symptom recognition**  
- **Patient data management** for personalized tracking  
- **Medical report uploads** & automated analysis  
- Integration with **computer vision pipelines** for real-time assessments  
- **Interactive AI assistant** for basic healthcare guidance  

---

## 🛠️ Tech Stack
<div align="center">
  <img src="https://skillicons.dev/icons?i=python" height="60" alt="Python"/>
  <img width="12"/>
  <img src="https://skillicons.dev/icons?i=opencv" height="60" alt="OpenCV"/>
  <img width="12"/>
  <img src="https://skillicons.dev/icons?i=html" height="60" alt="HTML"/>
  <img width="12"/>
  <img src="https://skillicons.dev/icons?i=css" height="60" alt="CSS"/>
  <img width="12"/>
  <img src="https://skillicons.dev/icons?i=javascript" height="60" alt="JavaScript"/>
  <img width="12"/>
  <img src="https://skillicons.dev/icons?i=flask" height="60" alt="Flask"/>
</div>

---

## 📝 How It Works
1. **Patient Interaction:** User inputs symptoms or uploads medical data.  
2. **AI Analysis:** LLMs and CV models analyze inputs and identify potential concerns.  
3. **Report Generation:** Generates suggestions, tracking reports, or alerts for healthcare staff.  
4. **Data Storage:** All patient interactions are saved securely for continuity.  

---


## 🚀 Installation & Usage
```bash
# Clone the repository
git clone https://github.com/parthdubz/ai-swasthya-sathi.git

# Navigate to the project folder
cd ai-swasthya-sathi

# Create virtual environment
python -m venv venv

# Activate environment (Windows)
venv\Scripts\activate

# Activate environment (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python ai.py
```
---
## 🏆 Achievement:
St. Xavier's SET Exhibition 30 — 1st Runner Up<br>
Apprecaiton Letter from Ripumardini Sainik Mahavidyalaya <br>
Apprecaiton Letter from Trinity College And SS <br>
Apprecaiton Letter from KIST College And SS
<br>

---
## Hardware used in the robot
ESP8266 <br>
Oled Display <br>
Speaker <br>
Microphone <br>
WEB Camera <br>
Buzzer <br>
LED <br>

---

## NEW UPDATE: AI V2

### Previous System Architecture

The previous version followed a sequential, turn-based workflow:

1. The user spoke through the microphone.
2. Speech was converted into text using Speech-to-Text.
3. Gemini AI processed the input and generated a Nepali response.
4. A short "please wait" message was played while processing.
5. The response was structured into four sections:
   - Empathy and acknowledgment
   - Possible reasons for symptoms
   - Simple self-care suggestions
   - Closing guidance

The system avoided providing direct diagnoses or prescribing medicines.

In the background, user interactions were stored securely in Supabase, including:
- User input text
- Detected symptom category
- Timestamp

Finally, the generated response was converted into speech using Text-to-Speech, and the system waited for the next user input.

**Old Pipeline:**

`User Voice → Speech-to-Text → Gemini AI Processing → Nepali Response Generation → Text-to-Speech`

### New System Architecture (AI V2)

The new version replaces the traditional turn-based pipeline with a **continuous duplex streaming architecture**, inspired by the **BaymaxLive system** from our latest project.

Instead of waiting for the complete user input and generating a response afterward:

- The microphone continuously streams audio input.
- Gemini processes the conversation in real time.
- The AI can generate responses while the user is still speaking.
- Audio output is streamed back in real-time chunks instead of waiting for a complete response.

This creates a more natural, interactive healthcare conversation experience with lower latency and smoother communication.

**New Pipeline:**

`Gemini Live Duplex Streaming (Microphone → Gemini AI → Speaker)`

**Result:**
A real-time Nepali healthcare AI assistant capable of natural voice conversations, faster responses, and a more human-like interaction experience.

---


https://github.com/user-attachments/assets/04df0eac-5f01-4ee1-b679-ee3503a69327


---

## 🌐 Connect with Us
<div align="center"> <a href="https://www.facebook.com/profile.php?id=61579786233519"> <img src="https://img.shields.io/badge/Facebook-%231877F2.svg?logo=Facebook&logoColor=white&style=for-the-badge"/> </a> 
  <a href="https://www.linkedin.com/in/parth-mahato"> <img src="https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=LinkedIn&logoColor=white&style=for-the-badge" alt="LinkedIn"/> </a> </div>
<br>

---
