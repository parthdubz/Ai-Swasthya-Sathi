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

## NEW UPDATE AI V2
-> HOW OLD SYSTEM USED TO WORK: <br>
The user speaks into the microphone, and their voice is converted into text. Gemini creates a Nepali reply while a short "please wait" message plays. The reply has four parts: empathy, possible reason, simple self-care advice, and a closing message... without giving a diagnosis or medicine. In the background, the system saves the user's text, symptom label, and time in Supabase for tracking. Finally, the AI speaks the answer aloud and waits for the next input.<br>
i.e.<br>
User Voice → Speech-to-Text → Gemini AI Processing → Nepali Response Generation → Text-to-Speech<br>

-> NEW SYSTEM MECHANISM:<br>
This replaces the old turn-based flow (record -> Google STT -> generate_content -> Edge TTS with a continuous duplex stream, modeled on BaymaxLive from baymax.py on our another latest project. The mic streams in constantly, Gemini can respond while you're still talking, and audio streams back out in chunks instead of waiting for one full reply to render.<br>
i.e.<br>
Gemini Live duplex streaming (mic → Gemini → speaker) = Nepali healthcare AI responses<br>


---


https://github.com/user-attachments/assets/04df0eac-5f01-4ee1-b679-ee3503a69327


---

## 🌐 Connect with Us
<div align="center"> <a href="https://www.facebook.com/profile.php?id=61579786233519"> <img src="https://img.shields.io/badge/Facebook-%231877F2.svg?logo=Facebook&logoColor=white&style=for-the-badge"/> </a> 
  <a href="https://www.linkedin.com/in/parth-mahato"> <img src="https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=LinkedIn&logoColor=white&style=for-the-badge" alt="LinkedIn"/> </a> </div>
<br>

---
