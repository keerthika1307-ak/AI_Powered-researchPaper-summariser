# 🧠 AI PaperIQ – Research Paper Summariser  
A Streamlit-based intelligent platform that extracts, analyzes, and summarises research papers using Gemini AI and Firebase authentication.  
This tool helps students, researchers, and professionals quickly understand research papers by generating short summaries, key points, and related insights.

---

## 🚀 Features

### 🔐 Authentication  
- User login & signup using **Firebase Authentication**  
- Secure key storage (ignored using `.gitignore`)

### 📄 PDF / URL Input  
- Upload research paper PDF files  
- Or fetch research papers directly using **Google Search + URL extraction**

### 🤖 AI-Powered Processing (Gemini API)  
- Generate Short Summary  
- Generate Detailed Summary  
- Extract Key Points  
- Extract Keywords  
- Title Suggestion  
- Explanation in Simple Language  
- Related Content Generation  
- JSON Response Parsing for multi-output formatting

### 📚 Multi-Page Streamlit UI  
- `home.py` → Main dashboard  
- `pages/` → Additional feature pages  
- Clean minimal UI for easy navigation  

### 🔥 Firebase Integration  
- Firebase Auth  
- Firebase Config (securely stored)  
- Can be extended to Firestore or Realtime DB for saving history  

### ⚙️ Utility Modules  
- `paper_fetcher.py` → Fetch and process paper URLs  
- `gemini_api.py` → AI calls, prompt handling, text extraction  
- `utils/` → Helper functions

---

## 🛠️ Tech Stack

### Frontend  
- **Streamlit** (UI framework)  
- Python (Core logic)

### Backend / Services  
- **Firebase Authentication**  
- **Gemini AI API** (LLM model for summarisation)  
- PDF Processing Libraries  

### Other Tools  
- GitHub for version control  
- Python virtual environment `.venv`

## 📂 Project Structure

AI_PaperIQ_Streamlit/
│── home.py
│── firebase_config.py
│── firebase_key.json (Ignored in Git)
│── utils/
│ ├── gemini_api.py
│ ├── paper_fetcher.py
│ └── init.py
│── pages/
│ ├── Summarise Paper.py
│ ├── Extract Key Points.py
│ └── ...
│── requirements.txt
│── README.md
└── .gitignore


---

## ▶️ How It Works (Workflow)

1. **User logs in** using Firebase Authentication  
2. **User uploads PDF** or enters a research paper URL  
3. PDF text extraction OR URL scraping occurs  
4. Extracted text is cleaned and passed to Gemini API  
5. Gemini generates:  
   - Summary  
   - Key points  
   - Keywords  
   - Simplified explanation  
   - Title suggestions  
6. Results displayed in Streamlit interface  

---

## 🧪 Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Infosys-Internship-Team-B/AI_Powered-researchPaper-summariser.git
cd AI_PaperIQ_Streamlit

2️⃣ Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Add Firebase Credentials

Create firebase_config.py and add your Firebase web config keys.

Create firebase_key.json for service account (IGNORED in Git).

5️⃣ Run the application
streamlit run home.py

🧩 Example Summary Output
📘 Title: Quantum Computing for Modern Cryptography

🧠 Summary:
- Quantum computing leverages superposition and entanglement.
- It promises exponential speedups in cryptographic tasks.
- Current challenges involve qubit stability and scalability.

📊 Insights:
1. Quantum algorithms can break RSA-like systems.
2. Post-quantum cryptography is a major research focus.
 
🔗 References:
- https://arxiv.org/abs/2107.04567
- 
💡 Future Enhancements
Multi-language summarization
Voice-based chatbot
In-depth semantic similarity heatmaps
Personalized research trend tracking


Passionate about AI, Data, and Software Development 💻✨
[#Infosys Springboard Virtual Internship Project]
